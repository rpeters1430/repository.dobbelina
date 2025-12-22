"""
Tests for url_dispatcher.py
Testing the URL dispatcher routing system
"""
import pytest
from unittest.mock import Mock, patch


class TestURLDispatcherInit:
    """Test URL_Dispatcher initialization"""

    def test_init_with_valid_module_name(self):
        """Test initialization with valid module name"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('testmodule')

        assert dispatcher.module_name == 'testmodule'
        assert dispatcher.img_search is not None
        assert dispatcher.img_cat is not None
        assert dispatcher.img_next is not None
        assert not dispatcher.widget

    def test_init_without_module_name(self):
        """Test initialization fails without module name"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        with pytest.raises(Exception, match="module name is required"):
            URL_Dispatcher('')

    def test_init_with_none_module_name(self):
        """Test initialization fails with None module name"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        with pytest.raises(Exception, match="module name is required"):
            URL_Dispatcher(None)

    def test_init_with_dot_in_module_name(self):
        """Test initialization fails with dot in module name"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        with pytest.raises(Exception, match="cannot contain . character"):
            URL_Dispatcher('module.name')


class TestGetFullMode:
    """Test get_full_mode() method"""

    def test_get_full_mode_with_simple_mode(self):
        """Test get_full_mode adds module prefix"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('mymodule')
        result = dispatcher.get_full_mode('List')

        assert result == 'mymodule.List'

    def test_get_full_mode_with_already_full_mode(self):
        """Test get_full_mode returns as-is when dot present"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('mymodule')
        result = dispatcher.get_full_mode('other.Function')

        assert result == 'other.Function'

    def test_get_full_mode_with_numeric_mode(self):
        """Test get_full_mode handles numeric mode"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('mymodule')
        result = dispatcher.get_full_mode(123)

        assert result == 'mymodule.123'


class TestRegister:
    """Test register() decorator"""

    def test_register_function(self):
        """Test registering a function"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        # Clear registries for clean test
        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        dispatcher = URL_Dispatcher('testmodule')

        @dispatcher.register()
        def test_function(arg1, arg2='default'):
            return "result"

        mode = 'testmodule.test_function'
        assert mode in URL_Dispatcher.func_registry
        assert URL_Dispatcher.func_registry[mode] == test_function
        assert 'arg1' in URL_Dispatcher.args_registry[mode]
        assert 'arg2' in URL_Dispatcher.kwargs_registry[mode]

    def test_register_function_without_args(self):
        """Test registering a function without arguments"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        dispatcher = URL_Dispatcher('testmodule')

        @dispatcher.register()
        def simple_function():
            pass

        mode = 'testmodule.simple_function'
        assert mode in URL_Dispatcher.func_registry
        assert URL_Dispatcher.args_registry[mode] == []
        assert URL_Dispatcher.kwargs_registry[mode] == []

    def test_register_function_all_kwargs(self):
        """Test registering a function with all keyword arguments"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        dispatcher = URL_Dispatcher('testmodule')

        @dispatcher.register()
        def kwargs_function(arg1='default1', arg2='default2'):
            pass

        mode = 'testmodule.kwargs_function'
        assert mode in URL_Dispatcher.func_registry
        assert URL_Dispatcher.args_registry[mode] == []
        assert len(URL_Dispatcher.kwargs_registry[mode]) == 2

    def test_register_idempotent(self):
        """Test re-registering same function is idempotent"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        dispatcher = URL_Dispatcher('testmodule')

        @dispatcher.register()
        def test_func():
            return "first"

        # Register again
        @dispatcher.register()
        def test_func():  # noqa: F811
            return "second"

        # Should not raise an error
        assert 'testmodule.test_func' in URL_Dispatcher.func_registry


class TestCoerce:
    """Test __coerce() static method"""

    def test_coerce_true_lowercase(self):
        """Test coercing 'true' to boolean"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('true')

        assert result is True

    def test_coerce_true_uppercase(self):
        """Test coercing 'TRUE' to boolean"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('TRUE')

        assert result is True

    def test_coerce_false_lowercase(self):
        """Test coercing 'false' to boolean"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('false')

        assert result is False

    def test_coerce_false_mixedcase(self):
        """Test coercing 'False' to boolean"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('False')

        assert result is False

    def test_coerce_none_string(self):
        """Test coercing 'none' to None"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('none')

        assert result is None

    def test_coerce_none_uppercase(self):
        """Test coercing 'NONE' to None"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('NONE')

        assert result is None

    def test_coerce_regular_string(self):
        """Test coercing regular string returns unchanged"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('hello world')

        assert result == 'hello world'

    def test_coerce_number_string(self):
        """Test coercing number string returns unchanged"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce('12345')

        assert result == '12345'

    def test_coerce_non_string(self):
        """Test coercing non-string returns unchanged"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        result = URL_Dispatcher._URL_Dispatcher__coerce(123)

        assert result == 123


class TestDispatch:
    """Test dispatch() class method"""

    def test_dispatch_function_with_args(self):
        """Test dispatching function with positional arguments"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        mock_func = Mock(return_value='result')
        mock_func.__name__ = 'test_func'

        # Manually register the mock
        mode = 'testmodule.test_func'
        URL_Dispatcher.func_registry[mode] = mock_func
        URL_Dispatcher.args_registry[mode] = ['arg1', 'arg2']
        URL_Dispatcher.kwargs_registry[mode] = []

        queries = {'arg1': 'value1', 'arg2': 'value2', 'mode': mode}
        URL_Dispatcher.dispatch(mode, queries)

        mock_func.assert_called_once_with('value1', 'value2')

    def test_dispatch_function_with_kwargs(self):
        """Test dispatching function with keyword arguments"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        mock_func = Mock()
        mode = 'testmodule.test_func'
        URL_Dispatcher.func_registry[mode] = mock_func
        URL_Dispatcher.args_registry[mode] = []
        URL_Dispatcher.kwargs_registry[mode] = ['opt1', 'opt2']

        queries = {'opt1': 'val1', 'opt2': 'val2', 'mode': mode}
        URL_Dispatcher.dispatch(mode, queries)

        mock_func.assert_called_once_with(opt1='val1', opt2='val2')

    def test_dispatch_function_mixed_args_kwargs(self):
        """Test dispatching with both args and kwargs"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        mock_func = Mock()
        mode = 'testmodule.mixed_func'
        URL_Dispatcher.func_registry[mode] = mock_func
        URL_Dispatcher.args_registry[mode] = ['required']
        URL_Dispatcher.kwargs_registry[mode] = ['optional']

        queries = {'required': 'req_val', 'optional': 'opt_val', 'mode': mode}
        URL_Dispatcher.dispatch(mode, queries)

        mock_func.assert_called_once_with('req_val', optional='opt_val')

    def test_dispatch_coerces_boolean_true(self):
        """Test dispatch coerces 'true' string to boolean"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        mock_func = Mock()
        mode = 'testmodule.bool_func'
        URL_Dispatcher.func_registry[mode] = mock_func
        URL_Dispatcher.args_registry[mode] = ['flag']
        URL_Dispatcher.kwargs_registry[mode] = []

        queries = {'flag': 'true', 'mode': mode}
        URL_Dispatcher.dispatch(mode, queries)

        mock_func.assert_called_once_with(True)

    def test_dispatch_unregistered_mode_raises_exception(self):
        """Test dispatching unregistered mode raises exception"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}

        with pytest.raises(Exception, match="unregistered mode"):
            URL_Dispatcher.dispatch('nonexistent.mode', {})

    def test_dispatch_missing_required_arg_raises_exception(self):
        """Test dispatching with missing required arg raises exception"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        mock_func = Mock()
        mode = 'testmodule.requires_arg'
        URL_Dispatcher.func_registry[mode] = mock_func
        URL_Dispatcher.args_registry[mode] = ['required_arg']
        URL_Dispatcher.kwargs_registry[mode] = []

        queries = {'mode': mode}  # Missing required_arg

        with pytest.raises(Exception, match="requested argument .* but it was not provided"):
            URL_Dispatcher.dispatch(mode, queries)

    def test_dispatch_ignores_extra_params(self):
        """Test dispatch ignores extra parameters"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        URL_Dispatcher.func_registry = {}
        URL_Dispatcher.args_registry = {}
        URL_Dispatcher.kwargs_registry = {}

        mock_func = Mock()
        mode = 'testmodule.simple'
        URL_Dispatcher.func_registry[mode] = mock_func
        URL_Dispatcher.args_registry[mode] = []
        URL_Dispatcher.kwargs_registry[mode] = []

        queries = {'mode': mode, 'extra': 'ignored', 'another': 'param'}
        URL_Dispatcher.dispatch(mode, queries)

        mock_func.assert_called_once_with()


class TestWrapperMethods:
    """Test wrapper methods (add_dir, add_download_link, etc.)"""

    @patch('resources.lib.url_dispatcher.addDir')
    def test_add_dir_calls_basics_addDir(self, mock_addDir):
        """Test add_dir calls basics.addDir with full mode"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('testsite')
        dispatcher.add_dir('Test Name', 'http://test.com', 'List', 'icon.png')

        mock_addDir.assert_called_once()
        call_args = mock_addDir.call_args[0]
        assert call_args[0] == 'Test Name'
        assert call_args[1] == 'http://test.com'
        assert call_args[2] == 'testsite.List'  # Mode should be prefixed

    @patch('resources.lib.url_dispatcher.addDir')
    def test_add_dir_with_widget_filters_next(self, mock_addDir):
        """Test add_dir with widget=True only shows Next pages"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('testsite')
        dispatcher.widget = True

        # Regular item should be filtered
        dispatcher.add_dir('Regular Item', 'http://test.com', 'List')
        assert mock_addDir.call_count == 0

        # Next page should pass through
        dispatcher.add_dir('Next Page', 'http://test.com/page2', 'List')
        assert mock_addDir.call_count == 1

    @patch('resources.lib.url_dispatcher.addDownLink')
    def test_add_download_link_calls_basics(self, mock_addDownLink):
        """Test add_download_link calls basics.addDownLink"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('testsite')
        dispatcher.add_download_link('Video', 'http://video.mp4', 'Playvid', 'thumb.jpg')

        mock_addDownLink.assert_called_once()
        call_args = mock_addDownLink.call_args[0]
        assert call_args[0] == 'Video'
        assert call_args[2] == 'testsite.Playvid'

    @patch('resources.lib.url_dispatcher.addDownLink')
    @patch('resources.lib.url_dispatcher.filter_listing', 'filtered;blocked')
    def test_add_download_link_filters_by_name(self, mock_addDownLink):
        """Test add_download_link filters items by name"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        # Reload to pick up the patched filter_listing
        import importlib
        import resources.lib.url_dispatcher as url_dispatcher_module
        importlib.reload(url_dispatcher_module)
        from resources.lib.url_dispatcher import URL_Dispatcher  # noqa: F811

        dispatcher = URL_Dispatcher('testsite')

        # This should be filtered
        dispatcher.add_download_link('This has filtered word', 'http://video.mp4', 'Playvid', 'thumb.jpg')

        # Should not be called because name contains 'filtered'
        assert mock_addDownLink.call_count == 0

    @patch('resources.lib.url_dispatcher.addImgLink')
    def test_add_img_link_calls_basics(self, mock_addImgLink):
        """Test add_img_link calls basics.addImgLink"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('testsite')
        dispatcher.add_img_link('Image', 'http://image.jpg', 'ShowImage')

        mock_addImgLink.assert_called_once()
        call_args = mock_addImgLink.call_args[0]
        assert call_args[0] == 'Image'
        assert call_args[2] == 'testsite.ShowImage'

    @patch('resources.lib.url_dispatcher.searchDir')
    def test_search_dir_calls_basics(self, mock_searchDir):
        """Test search_dir calls basics.searchDir"""
        from resources.lib.url_dispatcher import URL_Dispatcher

        dispatcher = URL_Dispatcher('testsite')
        dispatcher.search_dir('http://site.com', 'Search', page=1)

        mock_searchDir.assert_called_once()
        call_args = mock_searchDir.call_args[0]
        assert call_args[0] == 'http://site.com'
        assert call_args[1] == 'testsite.Search'
        assert call_args[2] == 1
