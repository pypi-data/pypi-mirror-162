"""
Utility routines that are useful for more than one package in the Jupyter
Physical Science Lab modules.
"""

######
# General initialization
######
notebookenv = "None"
temptext = ''
# update_notebook_env() will be called after it is defined below.

######
# JPSL Tools Menu
######

def JPSL_Tools_Menu():
    '''
    Installs and activates the JPSL Tools menu
    '''
    OTJS('JPSLUtils.createJPSLToolsMenu(); JPSLUtils.init();')
    pass

######
# Jupyter JS call utilities
#    Some of these are duplicated in pure javascript in the JPSLUtils.js file.
######
def OTJS(script):
    """
    aka: One Time Javascript.

    This wraps a call to display(JS(script)) so that it will not run again
    after 15 seconds have passed. This overcomes the way javascript from
    python is embedded in the notebook metadata. When a notebook with embedded
    javascript is reopened and trusted all the javascript calls are run again.
    This is fine for utility functions, but not necessarily things that are
    only expected to run if a particular cell is executed.
    :param script: valid javascript string.
    :return:
    """
    from IPython.display import display, Javascript as JS
    from time import time as baseseconds
    limit = 1000*(baseseconds()+15)
    scriptstr = """
    if (Date.now() > $LIMIT){
        //alert('old do not run')
    } else{
        $SCRIPT
    }
    """
    scriptstr = scriptstr.replace('$LIMIT',str(limit))
    scriptstr = scriptstr.replace('$SCRIPT',script)
    # print(scriptstr)
    display(JS(scriptstr))
    pass

def update_notebook_env(notebookenv):
    """
    Checks notebook environment. Calls javascript to check for
    Jupyter classic and Jupyter Lab. Sets JPSLUtils.notebookenv = colab|
    NBClassic|None. None is probably Jupyter Lab.
    :return:
    """
    from IPython import get_ipython
    user_ns = {}
    if get_ipython():
        user_ns = get_ipython().user_ns
    try:
        from google.colab import output
        notebookenv = 'colab'
        if "JPSLUtils" in user_ns:
            user_ns['JPSLUtils'].notebookenv = notebookenv
        return notebookenv
    except ModuleNotFoundError:
        pass
    if "JPSLUtils" in user_ns:
        notebookenv = user_ns['JPSLUtils'].notebookenv
    OTJS('JPSLUtils.getenv();')
    return notebookenv

def new_cell_immediately_below():
    """
    Inserts a new cell immediately below the currently selected cell.
    :return:
    """
    OTJS('Jupyter.notebook.focus_cell();' \
           'Jupyter.notebook.insert_cell_below();')
    pass


def select_cell_immediately_below():
    """
    Selects the cell below the currently selected cell.
    :return:
    """
    OTJS('Jupyter.notebook.select_next(true);')
    pass

def get_text_of_current_cell():
    OTJS("JPSLUtils.text_of_current_cell_to_Python(\"JPSLUtils.temptext\");")
    pass

def return_text_of_current_cell():
    return temptext

def move_cursor_in_current_cell(delta):
    """
    Moves the cursor by the amount delta in a codemirror cell.
    :param delta: change in cursor position.
    :return:
    """
    OTJS('var curPos = Jupyter.notebook.get_selected_cell().code_' \
           'mirror.doc.getCursor();' \
           'var curline = curPos.line; var curch = curPos.ch +' + str(
            delta) + ';' \
                     'Jupyter.notebook.get_selected_cell().code_mirror.' \
                     'doc.setCursor({line:curline,ch:curch});')
    pass

def escape_text_for_js(text):
    """
    To prevent issues in javascript escapes:
    \n to \\n,
    \" to \\"
    \' to \\'
    :param text:
    :return:
    """
    import re
    text = re.sub(r'\\n',r'\n',text)
    text = re.sub(r'\n',r'\\n',text)
    text = re.sub(r'\'',r'\'',text)
    text = re.sub(r'\"', r'\"', text)
    return text

def pseudoLatexToLatex(text):
    text = text.replace('%FRAC',r'\frac')
    text = text.replace('%EXP',r'\exp')
    text = text.replace('%SIN',r'\sin')
    text = text.replace('%LEFT',r'\left')
    text = text.replace('%RIGHT',r'\right')
    text = text.replace('%SQRT',r'\sqrt')
    text = text.replace('%PI',r'\pi')
    text = text.replace('%COLOR',r'\color')
    return(text);


def insert_text_into_next_cell(text):
    """
    Replaces the current selection in a codemirror cell with the contents of
    text.
    :param text: String to replace the selection with.
    :return:
    """
    text = escape_text_for_js(text)
    OTJS('Jupyter.notebook.select_next(true);' \
               'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
               'replaceSelection("' + text + '");')
    pass

def replace_text_of_next_cell(text):
    """
    Replaces the contents of the cell following the selected cell with the
    contents of text.
    :param text: String to replace the contents of the cell wtih.
    :return:
    """
    text = escape_text_for_js(text)
    cmdstr = 'Jupyter.notebook.select_next(true);' \
             'JPSLUtils.replace_text_of_current_cell("' + text + '");'
    # print(cmdstr)
    OTJS(cmdstr)

def replace_text_of_current_cell(text):
    """
    Replaces the contents of the currently selected cell with the contents
    of text.
    :param text: String to replace the contents of the cell with.
    :return:
    """
    text = escape_text_for_js(text)
    OTJS('JPSLUtils.replace_text_of_current_cell("' + text + '");')


def insert_text_at_beginning_of_current_cell(text):
    """
    Insert the contents of text at the beginning of the currently selected
    cell. Append \n to line insert as a separate line.
    :param text: String to insert into cell.
    :return:
    """
    text = escape_text_for_js(text)
    OTJS('Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'setCursor({line:0,ch:0});' \
           'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'replaceSelection("' + text + '");')
    pass


def insert_newline_at_end_of_current_cell(text):
    """
    Insert the contents of text as a newline at the end of the currently
    selected cell.
    :param text: String of the text to be added to the end of the cell.
    :return:
    """
    text = escape_text_for_js(text)
    OTJS('var lastline = Jupyter.notebook.get_selected_cell().' \
           'code_mirror.doc.lineCount();' \
           'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'setCursor(lastline,0);' \
           'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'replaceSelection("\\n' + text + '");')
    pass

def select_containing_cell(elemID):
    """
    Create a synthetic click in the cell to force selection of the cell
    containing the DOM element with the name matching the contents of elemID.
    :param elemID: String containing the id of the DOM element.
    :return:
    """
    OTJS('var elem = document.getElementById("'+elemID+'");' \
             'JPSLUtils.select_containing_cell(elem);')
    pass

def delete_selected_cell():
    """
    Deletes the selected cell.
    :return:
    """
    OTJS('Jupyter.notebook.delete_cell(' \
               'Jupyter.notebook.get_selected_index());')
    pass

######
# Bookkeeping and anti-cheating tools
######
def record_names_timestamp():
    """
    Creates a dialog to collect the names of the user and their partners.
    This is recorded permanently as a comment at the end of the cell where
    this is run. The cell should be protected, so that it cannot be
    accidentally deleted.
    :return:
    """
    from os import environ, uname
    from time import ctime
    from IPython.display import display, HTML
    userstr = 'Initialization -- Computer: ' + uname()[1] +' | User: ' + \
              environ['USER'] +  ' | Time: ' + ctime()
    display(HTML(
        '<div id="Last-User" style="font-weight:bold;">' + userstr +
        '</div>'))
    select_containing_cell("Last-User")
    OTJS('JPSLUtils.record_names()')
    pass

def timestamp():
    """
    Displays an HTML timestamp, with user and computer info in the output of
    the cell it is run in.
    :return:
    """
    from os import environ, uname
    from time import ctime
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    userstr = 'User: ' + environ['USER'] + ' | Computer: ' + \
              uname()[1] + ' | Time: ' + ctime()
    display(HTML(
        '<span id="Last-User" style="font-weight:bold;">' + userstr + '</span>'))
    pass

######
# User namespace diagnostics and module checking
######

def havepd():
    """
    Checks to see if pandas is imported into the ipython user namespace as pd.
    :return: True if the name pd refers to pandas, otherwise false.
    """
    from IPython import get_ipython
    tst1 = getattr(get_ipython().user_module,'pd', False)
    if tst1:
        return hasattr(tst1,'DataFrame')
    else:
        return tst1

def havenp():
    """
    Checks to see if numpy is imported into the ipython user namespace as np.
    :return: True if the name np refers to numpy, otherwise false.
    """
    from IPython import get_ipython
    tst1 = getattr(get_ipython().user_module,'np',False)
    if tst1:
        return hasattr(tst1,'nan')
    else:
        return tst1

######
# Pandas and Figures routines
######

def find_pandas_dataframe_names():
    """
    This operation will search the interactive name space for pandas
    DataFrame objects. It will not find DataFrames that are children
    of objects in the interactive namespace. You will need to provide
    your own operation for finding those.
    :return: list of string names for objects in the global interactive
    namespace that are pandas DataFrames.
    """
    from pandas import DataFrame as df
    from IPython import get_ipython

    dataframenames = []
    global_dict = get_ipython().user_ns
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k], df):
            dataframenames.append(k)
    return dataframenames

def find_figure_names():
    """
    This operation will search the interactive namespace for objects that are
    plotly Figures (plotly.graph_objects.Figure) or plotly FigureWidgets
    (plotly.graph_objects.FigureWidget). It will not find Figures or
    FigureWidgets that are children of other objects. You will need to
    provide your own operation for finding those.

    :return: list of string names for the objects in the global
    interactive namespace that are plotly Figures or FigureWidgets.
    """
    from plotly.graph_objects import Figure, FigureWidget
    from IPython import get_ipython

    fignames = []
    global_dict = get_ipython().user_ns
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k],
                                                       (Figure,FigureWidget)):
            fignames.append(k)
    return fignames

######
# Jupyter widget tools/extensions
######
class iconselector():
    """
    This class provides a self updating set of small buttons showing the
    font-awesome icons passed to it. The user selected icon is highlighted
    in darkgray. The `selected` attribute (value is a synonym) is set to the
    name of the current selection. The `box` attribute is an ipywidget HBox
    that can be displayed or incorporated into more complex ipywidget
    constructs to interact with the user.
    """
    #####
    # TODO: add .observe option to icon selector...change object to extend
    # the appropriate widget type?
    #####
    def __init__(self,iconlist, selected = None):
        """

        :param iconlist: list of string names for the font awsome icons to
        display. The names should not be prefixed with 'fa-'.
        :type iconlist: list of str
        :param selected: name of selected icon (default = None).
        :type selected: str
        """
        from ipywidgets import HBox, Button, Layout
        self.buttons = []
        self.selected = selected # This will be the selected icon name

        def iconbutclk(but):
            self.selected = but.icon
            for k in self.buttons:
                if k.icon != self.selected:
                    k.style.button_color = 'white'
                else:
                    k.style.button_color = 'darkgray'
            pass

        smallbut = Layout(width='30px')
        for k in iconlist:
            tempbut = Button(icon=k,layout=smallbut)
            tempbut.style.button_color = 'white'
            tempbut.style.boarder = 'none'
            tempbut.on_click(iconbutclk)
            self.buttons.append(tempbut)
        if self.selected != None:
            for k in self.buttons:
                if k.icon == self.selected:
                    iconbutclk(k)
        self.box = HBox(self.buttons) # This can be passed as a widget.

    @property
    def value(self):
        return self.selected

class notice_group():
    """
    A notice group contains a list of strings that are referred to by their
    index. The group keeps track of which notices are 'active'. A call to the
    `.notice_html()` method returns an unordered html formatted list of the
    notice texts. This can be used to display or update notice text
    for the user.

    Optional notice group color, header and footers can be provided.
    """
    def __init__(self, noticelist, header='', footer = '', color = ''):
        """

        :param noticelist: list of strings of the text for each notice
        :type noticelist: list
        :param header: string providing a header for this notice group
        :type header: str
        :param footer: string providing a footer for this notice group
        :type footer: str
        :param color: string compatible with css color attribute, used to
        color the displayed notices. The color not impact headers and footers.
        :type color: str
        """
        self.header = header
        self.noticelist = noticelist
        self.footer = footer
        self.color = color
        self.active = []

    def get_active(self):
        """Returns a list of indexes of active notices"""
        return self.active

    def set_active(self,whichnotices):
        """
        Used to set a specific list of notices to active. This will remove
        active notices that are not in the provided list.
        :param whichnotices:
        """
        self.active = whichnotices
        pass

    def activate_notice(self, notice_id):
        """
        adds one of the notices to the active list
        :param notice_id:
        :return:
        """
        if notice_id not in self.active:
            self.active.append(notice_id)
        pass

    def deactivate_notice(self, notice_id):
        """
        removes a notice from the active list
        :param notice_id:
        :return:
        """
        if notice_id in self.active:
            self.active.remove(notice_id)
        pass

    def notice_html(self):
        """
        Provides an html formatted string displaying the active notices.
        :return: string of html.
        """
        notice_header = ''
        if self.header !='':
            notice_header = '<h4 style="text-align:center;">'+self.header+\
                            ' </h4><ul>'
        notice_footer = self.footer+'</ul>'
        notice_txt = notice_header
        itemstart = '<li style="color:'+self.color+';">'
        for j in self.active:
            notice_txt += itemstart + self.noticelist[j]+'</li>'
        notice_txt += notice_footer
        return notice_txt

######
# Install JS support when this is imported with from JPSLUtils import *
######
import JPSLMenus # This loads the menu support javascript.
import os
from IPython.display import display, HTML

#Locate package directory
mydir=os.path.dirname(__file__) #absolute path to directory containing this file.

#load the supporting css
# tempcssfile = open(os.path.join(mydir,'css','input_table.css'))
# tempstyle = '<style type="text/css">'
# tempstyle += tempcssfile.read()+'</style>'
# tempcssfile.close()
# display(HTML(tempstyle))

#load the supporting javascript
tempJSfile=open(os.path.join(mydir,'javascript','JPSLUtils.js'))
tempscript='<script type="text/javascript">'
tempscript+=tempJSfile.read()+'</script>'
tempJSfile.close()
display(HTML(tempscript))
del tempJSfile
del tempscript
del mydir
del display
del HTML
del os

notebookenv = update_notebook_env(notebookenv)