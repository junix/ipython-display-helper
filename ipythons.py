def ipython_width(width:int):
    from IPython.display import display, HTML
    display(HTML(f"<style>.container {{ width:{width}% !important; }}</style>"))



"""Check if the code is running in Jupyter."""
try:
    match get_ipython().__class__.__name__:
        case "ZMQInteractiveShell":
            _style='default'
            _output_fmt = "html"
        case _:
            _style='monokai'
            _output_fmt = "terminal"
except NameError:
    _output_fmt = "terminal"


def highlight_source(
    code:str,
    *,
    style:str = _style,
    language:str='python', 
    output_fmt:str=_output_fmt,
) -> str:
    """Highlight source code."""
    from pygments import lexers,highlight   
    from pygments.styles import get_style_by_name,get_all_styles
    lexer = lexers.get_lexer_by_name(language)
    style = get_style_by_name(style)
    match output_fmt:
        case "html":
            from pygments.formatters.html import HtmlFormatter
            formatter = HtmlFormatter(full=True, style=style)
        case "terminal"|"term"|"terminal256":
            from pygments.formatters.terminal256 import Terminal256Formatter
            formatter = Terminal256Formatter(style=style)
        case _:
            raise ValueError(f"output_fmt must be 'html' or 'terminal', but got {output_fmt}.")
    return highlight(code, lexer, formatter)
    
def show_source(
    obj, 
    *,
    style:str = _style,
    language:str='python', 
    output_fmt:str=_output_fmt
):
    """Show source code of an object."""
    import inspect
    code = inspect.getsource(obj)
    highlight_code = highlight_source(code, style=style, language=language, output_fmt=output_fmt)
    # Highlight
    match output_fmt:
        case "html":
            from IPython.display import display_html, HTML
            display_html(HTML(highlight_code))
        case "terminal"|"term"|"terminal256":
            print(highlight_code)
        case _:
            raise ValueError(f"output_fmt must be 'html' or 'terminal', but got {output_fmt}.")
    