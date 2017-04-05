from rh_nexttask.renderer import Renderer

def test_renderer():
    a_renderer = Renderer(None)
    assert isinstance(a_renderer, Renderer)
