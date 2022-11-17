import maya.cmds as cmds
import maya.mel as mel
import os

from PySide2 import QtGui

NAME_WIDGET = 'BlurRelax_name'
RADIUS_WIDGET = 'BlurRelax_radius'
NEW_BIND_MESH_WIDGET = 'BlurRelax_newbindmesh'
BIND_FILE_WIDGET = 'BlurRelax_bindfile'
MENU_ITEMS = []


def create_menuitems():
    global MENU_ITEMS
    if MENU_ITEMS:
        # Already created
        return
    if cmds.about(api=True) < 201600:
        cmds.warning('BlurRelax menus only available in Maya 2016 and higher.')
        return
    for menu in ['mainDeformMenu', 'mainRigDeformationsMenu']:
        # Make sure the menu widgets exist first.
        mel.eval('ChaDeformationsMenu MayaWindow|{0};'.format(menu))
        items = cmds.menu(menu, q=True, ia=True)
        for item in items:
            if cmds.menuItem(item, q=True, divider=True):
                section = cmds.menuItem(item, q=True, label=True)
            menu_label = cmds.menuItem(item, q=True, label=True)
            if menu_label == 'Delta Mush':
                if section == 'Create':
                    BlurRelax_item = cmds.menuItem(
                        label="BlurRelax",
                        command=create_blur_relax,
                        sourceType='python',
                        insertAfter=item,
                        parent=menu,
                    )
                    BlurRelax_options = cmds.menuItem(
                        command=display_blur_relax_options,
                        insertAfter=BlurRelax_item,
                        parent=menu,
                        optionBox=True,
                    )
                    MENU_ITEMS.append(BlurRelax_item)
                    MENU_ITEMS.append(BlurRelax_options)
            elif menu_label == 'Delta Mush' and section == 'Paint Weights':
                item = cmds.menuItem(
                    label="BlurRelax",
                    command=paint_blur_relax_weights,
                    sourceType='python',
                    insertAfter=item,
                    parent=menu,
                )
                MENU_ITEMS.append(item)


def create_blur_relax(*args, **kwargs):
    cmds.loadPlugin('BlurRelax', quiet=True)
    nodes = cmds.deformer(type="BlurRelax")
    kwargs = get_create_command_kwargs()
    for node in nodes:
        for attr, value in kwargs.items():
            cmds.setAttr("{0}.{1}".format(node, attr), value)


def get_create_command_kwargs():
    """Gets the BlurRelax command arguments either from the option box widgets or the saved
    option vars.  If the widgets exist, their values will be saved to the option vars.
    @return A dictionary of the kwargs to the BlurRelax command."""
    args = {}
    if cmds.textFieldGrp(NAME_WIDGET, exists=True):
        args['name'] = cmds.textFieldGrp(NAME_WIDGET, q=True, text=True)
        cmds.optionVar(sv=(NAME_WIDGET, args['name']))
    else:
        args['name'] = cmds.optionVar(q=NAME_WIDGET) or 'BlurRelax#'
    if cmds.floatSliderGrp(RADIUS_WIDGET, exists=True):
        args['radius'] = cmds.floatSliderGrp(RADIUS_WIDGET, q=True, value=True)
        cmds.optionVar(fv=(RADIUS_WIDGET, args['radius']))
    else:
        args['radius'] = cmds.optionVar(q=RADIUS_WIDGET)

    if cmds.checkBoxGrp(NEW_BIND_MESH_WIDGET, exists=True):
        if cmds.checkBoxGrp(NEW_BIND_MESH_WIDGET, q=True, v1=True):
            args['newBindMesh'] = True
            cmds.optionVar(iv=(NEW_BIND_MESH_WIDGET, 1))
        else:
            cmds.optionVar(iv=(NEW_BIND_MESH_WIDGET, 0))
    else:
        value = cmds.optionVar(q=NEW_BIND_MESH_WIDGET)
        if value:
            args['newBindMesh'] = True

    if cmds.textFieldButtonGrp(BIND_FILE_WIDGET, exists=True):
        bind_file = cmds.textFieldButtonGrp(BIND_FILE_WIDGET, q=True, text=True)
        bind_file = os.path.expandvars(bind_file.strip())
        if bind_file:
            if os.path.exists(bind_file):
                args['binding'] = bind_file
            else:
                cmds.warning('{0} does not exist.'.format(bind_file))

    return args


def display_blur_relax_options(*args, **kwargs):
    cmds.loadPlugin('BlurRelax', qt=True)
    layout = mel.eval('getOptionBox')
    cmds.setParent(layout)
    cmds.columnLayout(adj=True)

    for widget in [NAME_WIDGET, RADIUS_WIDGET, BIND_FILE_WIDGET, NEW_BIND_MESH_WIDGET]:
        # Delete the widgets so we don't create multiple controls with the same name
        try:
            cmds.deleteUI(widget, control=True)
        except RuntimeError:
            pass

    cmds.textFieldGrp(NAME_WIDGET, label='Node name', text='BlurRelax#')
    radius = cmds.optionVar(q=RADIUS_WIDGET)
    cmds.floatSliderGrp(
        RADIUS_WIDGET,
        label='Sample radius',
        field=True,
        minValue=0.0,
        maxValue=100.0,
        fieldMinValue=0.0,
        fieldMaxValue=100.0,
        value=radius,
        step=0.01,
        precision=2,
    )
    cmds.textFieldButtonGrp(
        BIND_FILE_WIDGET,
        label='Binding file ',
        text='',
        buttonLabel='Browse',
        bc=display_bind_file_dialog,
    )
    use_new_bind_mesh = cmds.optionVar(q=NEW_BIND_MESH_WIDGET)
    cmds.checkBoxGrp(
        NEW_BIND_MESH_WIDGET,
        numberOfCheckBoxes=1,
        label='Create new bind mesh',
        v1=use_new_bind_mesh,
    )


    mel.eval('setOptionBoxTitle("BlurRelax Options");')
    mel.eval('setOptionBoxCommandName("BlurRelax");')
    apply_close_button = mel.eval('getOptionBoxApplyAndCloseBtn;')
    cmds.button(apply_close_button, e=True, command=apply_and_close)
    apply_button = mel.eval('getOptionBoxApplyBtn;')
    cmds.button(apply_button, e=True, command=create_blur_relax)
    reset_button = mel.eval('getOptionBoxResetBtn;')
    # For some reason, the buttons in the menu only accept MEL.
    cmds.button(
        reset_button,
        e=True,
        command='python("import BlurRelax.menu; blurRelax.menu.reset_to_defaults()");',
    )
    close_button = mel.eval('getOptionBoxCloseBtn;')
    cmds.button(close_button, e=True, command=close_option_box)
    save_button = mel.eval('getOptionBoxSaveBtn;')
    cmds.button(
        save_button,
        e=True,
        command='python("import BlurRelax.menu; blurRelax.menu.get_create_command_kwargs()");',
    )
    mel.eval('showOptionBox')


def apply_and_close(*args, **kwargs):
    """Create the BlurRelax deformer and close the option box."""
    create_blur_relax()
    mel.eval('saveOptionBoxSize')
    close_option_box()


def close_option_box(*args, **kwargs):
    mel.eval('hideOptionBox')


def display_bind_file_dialog(*args, **kwargs):
    """Displays the dialog to choose the binding file with which to create the BlurRelax deformer."""
    root_dir = cmds.workspace(q=True, rootDirectory=True)
    start_directory = os.path.join(root_dir, 'data')
    file_path = cmds.fileDialog2(
        fileFilter='*.wrap',
        dialogStyle=2,
        fileMode=1,
        startingDirectory=start_directory,
    )
    if file_path:
        cmds.textFieldButtonGrp(BIND_FILE_WIDGET, e=True, text=file_path[0])


def reset_to_defaults(*args, **kwargs):
    """Reset the BlurRelax option box widgets to their defaults."""
    cmds.textFieldGrp(NAME_WIDGET, e=True, text='BlurRelax#')
    cmds.floatSliderGrp(RADIUS_WIDGET, e=True, value=0)
    cmds.textFieldButtonGrp(BIND_FILE_WIDGET, e=True, text='')
    cmds.checkBoxGrp(NEW_BIND_MESH_WIDGET, e=True, v1=False)


def get_wrap_node_from_object(obj):
    """Get a wrap node from the selected geometry."""
    if cmds.nodeType(obj) == 'BlurRelax':
        return obj
    history = cmds.listHistory(obj, pdo=0) or []
    wrap_nodes = [node for node in history if cmds.nodeType(node) == 'BlurRelax']
    if not wrap_nodes:
        raise RuntimeError('No BlurRelax node found on {0}.'.format(obj))
    if len(wrap_nodes) == 1:
        return wrap_nodes[0]
    else:
        # Multiple wrap nodes are deforming the mesh.  Let the user choose which one
        # to use.
        return QtGui.QInputDialog.getItem(
            None, 'Select BlurRelax node', 'blurRelax node:', wrap_nodes
        )


def get_wrap_node_from_selected():
    """Get a wrap node from the selected geometry."""
    sel = cmds.ls(sl=True) or []
    if not sel:
        raise RuntimeError('No BlurRelax found on selected.')
    return get_wrap_node_from_object(sel[0])


def destroy_menuitems():
    """Remove the BlurRelax items from the menus."""
    global MENU_ITEMS
    for item in MENU_ITEMS:
        cmds.deleteUI(item, menuItem=True)
    MENU_ITEMS = []


def paint_blur_relax_weights(*args, **kwargs):
    """Activates the paint BlurRelax weights context."""
    sel = cmds.ls(sl=True)
    if sel:
        wrap_node = get_wrap_node_from_selected()
        if wrap_node:
            mel.eval(
                'artSetToolAndSelectAttr("artAttrCtx", "BlurRelax.{0}.weights");'.format(
                    wrap_node
                )
            )
