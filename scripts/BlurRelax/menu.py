import os
from maya import cmds, mel
from PySide2 import QtGui

MENU_ITEMS = None


def get_relax_node_on_object(obj):
    if cmds.nodeType(obj) == 'BlurRelax':
        return obj
    history = cmds.listHistory(obj, pdo=0) or []
    wrap_nodes = [node for node in history if cmds.nodeType(node) == 'cvWrap']
    if not wrap_nodes:
        raise RuntimeError('No cvWrap node found on {0}.'.format(obj))
    if len(wrap_nodes) == 1:
        return wrap_nodes[0]
    else:
        # Multiple wrap nodes are deforming the mesh.  Let the user choose which one
        # to use.
        return QtGui.QInputDialog.getItem(
            None, 'Select cvWrap node', 'cvWrap node:', wrap_nodes
        )

def get_relax_node_from_selected():
    sel = cmds.ls(sl=True) or []
    if not sel:
        raise RuntimeError('No cvWrap found on selected.')
    return get_relax_node_on_object(sel[0])


NAME_WIDGET = 'cvwrap_name'
RADIUS_WIDGET = 'cvwrap_radius'
NEW_BIND_MESH_WIDGET = 'cvwrap_newbindmesh'
BIND_FILE_WIDGET = 'cvwrap_bindfile'
def get_create_options():
    """Gets the cvWrap command arguments either from the option box widgets or the saved
    option vars.  If the widgets exist, their values will be saved to the option vars.
    @return A dictionary of the kwargs to the cvWrap command."""
    args = {}
    if cmds.textFieldGrp(NAME_WIDGET, exists=True):
        args['name'] = cmds.textFieldGrp(NAME_WIDGET, q=True, text=True)
        cmds.optionVar(sv=(NAME_WIDGET, args['name']))
    else:
        args['name'] = cmds.optionVar(q=NAME_WIDGET) or 'cvWrap#'
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







def set_attr_values(nodes):
    pass

def create_blur_relax(*args, **kwargs):
    cmds.loadPlugin('BlurRelax', quiet=True)
    nodes = cmds.deformer(type="BlurRelax")
    set_attr_values(nodes)











def create_blur_relax_opts(*args, **kwargs):
    cmds.loadPlugin('BlurRelax', quiet=True)
    layout = mel.eval('getOptionBox')
    cmds.setParent(layout)
    cmds.columnLayout(adj=True)

    for widget in []:
        # Delete the widgets so we don't create multiple controls with the same name
        try:
            cmds.deleteUI(widget, control=True)
        except RuntimeError:
            pass


    borderOpt = cmds.optionMenu(label="Border Behavior")
    cmds.menuItem(label="None", parent=borderOpt)
    cmds.menuItem(label="Pin", parent=borderOpt)
    cmds.menuItem(label="Slide", parent=borderOpt)

    hardOpt = cmds.optionMenu(label="Hard Edge Behavior")
    cmds.menuItem(label="None", parent=hardOpt)
    cmds.menuItem(label="Pin", parent=hardOpt)
    cmds.menuItem(label="Slide", parent=hardOpt)

    groupOpt = cmds.optionMenu(label="Group Edge Behavior")
    cmds.menuItem(label="None", parent=groupOpt)
    cmds.menuItem(label="Pin", parent=groupOpt)
    cmds.menuItem(label="Slide", parent=groupOpt)

    cmds.checkBoxGrp(
        numberOfCheckBoxes=1,
        label='reproject',
        #value1=use_new_bind_mesh,
    )

    cmds.floatSliderGrp(
        label='Reproject Divs',
        field=True,
        minValue=0,
        maxValue=3,
        fieldMinValue=0,
        fieldMaxValue=3,
        step=1,
        precision=0,
    )

    cmds.floatSliderGrp(
        label='Preserve Volume',
        field=True,
        minValue=0.0,
        maxValue=2.0,
        fieldMinValue=0.0,
        fieldMaxValue=2.0,
        step=0.01,
        precision=2,
    )

    cmds.floatSliderGrp(
        label='Iterations',
        field=True,
        minValue=0.0,
        maxValue=50.0,
        fieldMinValue=0.0,
        fieldMaxValue=1000.0,
        step=0.1,
        precision=1,
    )

    cmds.floatSliderGrp(
        label='Preserve Volume',
        field=True,
        minValue=0.0,
        maxValue=2.0,
        fieldMinValue=0.0,
        fieldMaxValue=2.0,
        step=0.01,
        precision=2,
    )

    cmds.checkBoxGrp(
        numberOfCheckBoxes=1,
        label='Delta',
        #value1=use_new_bind_mesh,
    )
    cmds.floatSliderGrp(
        label='Delta Multiplier',
        field=True,
        minValue=0.0,
        maxValue=1.0,
        fieldMinValue=0.0,
        fieldMaxValue=10.0,
        step=0.1,
        precision=1,
    )





    mel.eval('setOptionBoxTitle("cvWrap Options");')
    mel.eval('setOptionBoxCommandName("cvWrap");')
    apply_close_button = mel.eval('getOptionBoxApplyAndCloseBtn;')
    cmds.button(apply_close_button, e=True, command=apply_and_close)
    apply_button = mel.eval('getOptionBoxApplyBtn;')
    cmds.button(apply_button, e=True, command=create_cvwrap)
    reset_button = mel.eval('getOptionBoxResetBtn;')
    # For some reason, the buttons in the menu only accept MEL.
    cmds.button(
        reset_button,
        e=True,
        command='python("import cvwrap.menu; cvwrap.menu.reset_to_defaults()");',
    )
    close_button = mel.eval('getOptionBoxCloseBtn;')
    cmds.button(close_button, e=True, command=close_option_box)
    save_button = mel.eval('getOptionBoxSaveBtn;')
    cmds.button(
        save_button,
        e=True,
        command='python("import cvwrap.menu; cvwrap.menu.get_create_command_kwargs()");',
    )
    mel.eval('showOptionBox')







def paint_blur_relax():
    """Activates the paint weights context."""
    sel = cmds.ls(sl=True)
    if not sel:
        return
    wrap_node = get_relax_node_from_selected()
    if not wrap_node:
        return
    mel.eval(
        'artSetToolAndSelectAttr("artAttrCtx", "cvWrap.{0}.weights");'.format(
            wrap_node
        )
    )



def create_menuitems():
    global MENU_ITEMS
    if MENU_ITEMS is not None:
        # Already created
        return

    for menu in ['mainDeformMenu', 'mainRigDeformationsMenu']:
        # Make sure the menu widgets exist first.
        mel.eval('ChaDeformationsMenu MayaWindow|{0};'.format(menu))
        items = cmds.menu(menu, query=True, itemArray=True)
        for item in items:
            if cmds.menuItem(item, query=True, divider=True):
                section = cmds.menuItem(item, query=True, label=True)
            menu_label = cmds.menuItem(item, query=True, label=True)

            if menu_label == 'Delta Mush':
                if section == 'Create':
                    create_item = cmds.menuItem(
                        label='Blur Relax',
                        command=create_blur_relax,
                        sourceType='python',
                        insertAfter=item,
                        parent=menu,
                    )
                    option_item = cmds.menuItem(
                        command=create_blur_relax_opts,
                        sourceType='python',
                        insertAfter=create_item,
                        parent=menu,
                        optionBox=True,
                    )
                    MENU_ITEMS.append(create_item)
                    MENU_ITEMS.append(option_item)
                elif section == 'Paint Weights':
                    paint_item = cmds.menuItem(
                        label='Blur Relax',
                        command=paint_blur_relax,
                        sourceType='python',
                        insertAfter=item,
                        parent=menu,
                    )
                    paint_opt_item = cmds.menuItem(
                        command=paint_blur_relax,
                        sourceType='python',
                        insertAfter=paint_item,
                        parent=menu,
                        optionBox=True,
                    )
                    MENU_ITEMS.append(paint_item)
                    MENU_ITEMS.append(paint_opt_item)
