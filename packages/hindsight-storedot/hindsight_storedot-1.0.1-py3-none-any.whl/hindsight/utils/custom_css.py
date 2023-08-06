from IPython.core.display import HTML
from IPython.display import display, Javascript

def inject_css(*args):
    style = """
    <style>
    {arguments}
    </style>
    """.format(arguments=''.join(args))
    display(HTML(style))

def kernel_spinner():
    return inject_css("""
    @keyframes spinner {
        0% {
            transform: translate3d(-50%, -50%, 0) rotate(0deg);
            visibility:hidden;
        }
        5% {
            transform: translate3d(-50%, -50%, 0) rotate(72deg);
            visibility:hidden;
        }
        100% {
            transform: translate3d(-50%, -50%, 0) rotate(1440deg);
            visibility:visible;
        }
        }
        div[data-status="busy"]:before {
        animation: 20s linear infinite spinner;
        animation-play-state: inherit;
        border: solid 5px #cfd0d1;
        border-bottom-color: #1c87c9;
        border-radius: 50%;
        content: "";
        height: 50px;
        width: 50px;
        position: absolute;
        top: 10%;
        left: 10%;
        transform: translate3d(-50%, -50%, 0);
        will-change: transform;
        position: fixed;
        top: 50%;
        left: 50%;
    }
    """)

def bokeh_transparent_button():
    return inject_css("""
    .bk-root .bk-btn-default {
        border-radius: 0px;
        opacity: 0.5;
        font-weight: bolder;
     }
    """)

