(self["webpackChunkblack_knight"] = self["webpackChunkblack_knight"] || []).push([[179],{

/***/ 2584:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
// ESM COMPAT FLAG
__webpack_require__.r(__webpack_exports__);

// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  "__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED": () => (/* binding */ __SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED),
  "default": () => (/* binding */ loadable_esm),
  "lazy": () => (/* binding */ lazy$2),
  "loadableReady": () => (/* binding */ loadableReady)
});

// EXTERNAL MODULE: ./node_modules/react/index.js
var react = __webpack_require__(7294);
;// CONCATENATED MODULE: ./node_modules/@babel/runtime/helpers/esm/objectWithoutPropertiesLoose.js
function _objectWithoutPropertiesLoose(source, excluded) {
  if (source == null) return {};
  var target = {};
  var sourceKeys = Object.keys(source);
  var key, i;

  for (i = 0; i < sourceKeys.length; i++) {
    key = sourceKeys[i];
    if (excluded.indexOf(key) >= 0) continue;
    target[key] = source[key];
  }

  return target;
}
// EXTERNAL MODULE: ./node_modules/@babel/runtime/helpers/esm/extends.js
var esm_extends = __webpack_require__(7462);
;// CONCATENATED MODULE: ./node_modules/@babel/runtime/helpers/esm/assertThisInitialized.js
function _assertThisInitialized(self) {
  if (self === void 0) {
    throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  }

  return self;
}
;// CONCATENATED MODULE: ./node_modules/@babel/runtime/helpers/esm/setPrototypeOf.js
function _setPrototypeOf(o, p) {
  _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) {
    o.__proto__ = p;
    return o;
  };

  return _setPrototypeOf(o, p);
}
;// CONCATENATED MODULE: ./node_modules/@babel/runtime/helpers/esm/inheritsLoose.js

function _inheritsLoose(subClass, superClass) {
  subClass.prototype = Object.create(superClass.prototype);
  subClass.prototype.constructor = subClass;
  _setPrototypeOf(subClass, superClass);
}
// EXTERNAL MODULE: ./node_modules/react-is/index.js
var react_is = __webpack_require__(9864);
// EXTERNAL MODULE: ./node_modules/hoist-non-react-statics/dist/hoist-non-react-statics.cjs.js
var hoist_non_react_statics_cjs = __webpack_require__(8679);
var hoist_non_react_statics_cjs_default = /*#__PURE__*/__webpack_require__.n(hoist_non_react_statics_cjs);
;// CONCATENATED MODULE: ./node_modules/@loadable/component/dist/loadable.esm.js








/* eslint-disable import/prefer-default-export */
function invariant(condition, message) {
  if (condition) return;
  var error = new Error("loadable: " + message);
  error.framesToPop = 1;
  error.name = 'Invariant Violation';
  throw error;
}
function warn(message) {
  // eslint-disable-next-line no-console
  console.warn("loadable: " + message);
}

var Context = /*#__PURE__*/
react.createContext();

var LOADABLE_REQUIRED_CHUNKS_KEY = '__LOADABLE_REQUIRED_CHUNKS__';
function getRequiredChunkKey(namespace) {
  return "" + namespace + LOADABLE_REQUIRED_CHUNKS_KEY;
}

var sharedInternals = /*#__PURE__*/Object.freeze({
  __proto__: null,
  getRequiredChunkKey: getRequiredChunkKey,
  invariant: invariant,
  Context: Context
});

var LOADABLE_SHARED = {
  initialChunks: {}
};

var STATUS_PENDING = 'PENDING';
var STATUS_RESOLVED = 'RESOLVED';
var STATUS_REJECTED = 'REJECTED';

function resolveConstructor(ctor) {
  if (typeof ctor === 'function') {
    return {
      requireAsync: ctor,
      resolve: function resolve() {
        return undefined;
      },
      chunkName: function chunkName() {
        return undefined;
      }
    };
  }

  return ctor;
}

var withChunkExtractor = function withChunkExtractor(Component) {
  var LoadableWithChunkExtractor = function LoadableWithChunkExtractor(props) {
    return react.createElement(Context.Consumer, null, function (extractor) {
      return react.createElement(Component, Object.assign({
        __chunkExtractor: extractor
      }, props));
    });
  };

  if (Component.displayName) {
    LoadableWithChunkExtractor.displayName = Component.displayName + "WithChunkExtractor";
  }

  return LoadableWithChunkExtractor;
};

var identity = function identity(v) {
  return v;
};

function createLoadable(_ref) {
  var _ref$defaultResolveCo = _ref.defaultResolveComponent,
      defaultResolveComponent = _ref$defaultResolveCo === void 0 ? identity : _ref$defaultResolveCo,
      _render = _ref.render,
      onLoad = _ref.onLoad;

  function loadable(loadableConstructor, options) {
    if (options === void 0) {
      options = {};
    }

    var ctor = resolveConstructor(loadableConstructor);
    var cache = {};
    /**
     * Cachekey represents the component to be loaded
     * if key changes - component has to be reloaded
     * @param props
     * @returns {null|Component}
     */

    function _getCacheKey(props) {
      if (options.cacheKey) {
        return options.cacheKey(props);
      }

      if (ctor.resolve) {
        return ctor.resolve(props);
      }

      return 'static';
    }
    /**
     * Resolves loaded `module` to a specific `Component
     * @param module
     * @param props
     * @param Loadable
     * @returns Component
     */


    function resolve(module, props, Loadable) {
      var Component = options.resolveComponent ? options.resolveComponent(module, props) : defaultResolveComponent(module);

      if (options.resolveComponent && !(0,react_is.isValidElementType)(Component)) {
        throw new Error("resolveComponent returned something that is not a React component!");
      }

      hoist_non_react_statics_cjs_default()(Loadable, Component, {
        preload: true
      });
      return Component;
    }

    var cachedLoad = function cachedLoad(props) {
      var cacheKey = _getCacheKey(props);

      var promise = cache[cacheKey];

      if (!promise || promise.status === STATUS_REJECTED) {
        promise = ctor.requireAsync(props);
        promise.status = STATUS_PENDING;
        cache[cacheKey] = promise;
        promise.then(function () {
          promise.status = STATUS_RESOLVED;
        }, function (error) {
          console.error('loadable-components: failed to asynchronously load component', {
            fileName: ctor.resolve(props),
            chunkName: ctor.chunkName(props),
            error: error ? error.message : error
          });
          promise.status = STATUS_REJECTED;
        });
      }

      return promise;
    };

    var InnerLoadable =
    /*#__PURE__*/
    function (_React$Component) {
      _inheritsLoose(InnerLoadable, _React$Component);

      InnerLoadable.getDerivedStateFromProps = function getDerivedStateFromProps(props, state) {
        var cacheKey = _getCacheKey(props);

        return (0,esm_extends/* default */.Z)({}, state, {
          cacheKey: cacheKey,
          // change of a key triggers loading state automatically
          loading: state.loading || state.cacheKey !== cacheKey
        });
      };

      function InnerLoadable(props) {
        var _this;

        _this = _React$Component.call(this, props) || this;
        _this.state = {
          result: null,
          error: null,
          loading: true,
          cacheKey: _getCacheKey(props)
        };
        invariant(!props.__chunkExtractor || ctor.requireSync, 'SSR requires `@loadable/babel-plugin`, please install it'); // Server-side

        if (props.__chunkExtractor) {
          // This module has been marked with no SSR
          if (options.ssr === false) {
            return _assertThisInitialized(_this);
          } // We run load function, we assume that it won't fail and that it
          // triggers a synchronous loading of the module


          ctor.requireAsync(props)["catch"](function () {
            return null;
          }); // So we can require now the module synchronously

          _this.loadSync();

          props.__chunkExtractor.addChunk(ctor.chunkName(props));

          return _assertThisInitialized(_this);
        } // Client-side with `isReady` method present (SSR probably)
        // If module is already loaded, we use a synchronous loading
        // Only perform this synchronous loading if the component has not
        // been marked with no SSR, else we risk hydration mismatches


        if (options.ssr !== false && ( // is ready - was loaded in this session
        ctor.isReady && ctor.isReady(props) || // is ready - was loaded during SSR process
        ctor.chunkName && LOADABLE_SHARED.initialChunks[ctor.chunkName(props)])) {
          _this.loadSync();
        }

        return _this;
      }

      var _proto = InnerLoadable.prototype;

      _proto.componentDidMount = function componentDidMount() {
        this.mounted = true; // retrieve loading promise from a global cache

        var cachedPromise = this.getCache(); // if promise exists, but rejected - clear cache

        if (cachedPromise && cachedPromise.status === STATUS_REJECTED) {
          this.setCache();
        } // component might be resolved synchronously in the constructor


        if (this.state.loading) {
          this.loadAsync();
        }
      };

      _proto.componentDidUpdate = function componentDidUpdate(prevProps, prevState) {
        // Component has to be reloaded on cacheKey change
        if (prevState.cacheKey !== this.state.cacheKey) {
          this.loadAsync();
        }
      };

      _proto.componentWillUnmount = function componentWillUnmount() {
        this.mounted = false;
      };

      _proto.safeSetState = function safeSetState(nextState, callback) {
        if (this.mounted) {
          this.setState(nextState, callback);
        }
      }
      /**
       * returns a cache key for the current props
       * @returns {Component|string}
       */
      ;

      _proto.getCacheKey = function getCacheKey() {
        return _getCacheKey(this.props);
      }
      /**
       * access the persistent cache
       */
      ;

      _proto.getCache = function getCache() {
        return cache[this.getCacheKey()];
      }
      /**
       * sets the cache value. If called without value sets it as undefined
       */
      ;

      _proto.setCache = function setCache(value) {
        if (value === void 0) {
          value = undefined;
        }

        cache[this.getCacheKey()] = value;
      };

      _proto.triggerOnLoad = function triggerOnLoad() {
        var _this2 = this;

        if (onLoad) {
          setTimeout(function () {
            onLoad(_this2.state.result, _this2.props);
          });
        }
      }
      /**
       * Synchronously loads component
       * target module is expected to already exists in the module cache
       * or be capable to resolve synchronously (webpack target=node)
       */
      ;

      _proto.loadSync = function loadSync() {
        // load sync is expecting component to be in the "loading" state already
        // sounds weird, but loading=true is the initial state of InnerLoadable
        if (!this.state.loading) return;

        try {
          var loadedModule = ctor.requireSync(this.props);
          var result = resolve(loadedModule, this.props, Loadable);
          this.state.result = result;
          this.state.loading = false;
        } catch (error) {
          console.error('loadable-components: failed to synchronously load component, which expected to be available', {
            fileName: ctor.resolve(this.props),
            chunkName: ctor.chunkName(this.props),
            error: error ? error.message : error
          });
          this.state.error = error;
        }
      }
      /**
       * Asynchronously loads a component.
       */
      ;

      _proto.loadAsync = function loadAsync() {
        var _this3 = this;

        var promise = this.resolveAsync();
        promise.then(function (loadedModule) {
          var result = resolve(loadedModule, _this3.props, Loadable);

          _this3.safeSetState({
            result: result,
            loading: false
          }, function () {
            return _this3.triggerOnLoad();
          });
        })["catch"](function (error) {
          return _this3.safeSetState({
            error: error,
            loading: false
          });
        });
        return promise;
      }
      /**
       * Asynchronously resolves(not loads) a component.
       * Note - this function does not change the state
       */
      ;

      _proto.resolveAsync = function resolveAsync() {
        var _this$props = this.props,
            __chunkExtractor = _this$props.__chunkExtractor,
            forwardedRef = _this$props.forwardedRef,
            props = _objectWithoutPropertiesLoose(_this$props, ["__chunkExtractor", "forwardedRef"]);

        return cachedLoad(props);
      };

      _proto.render = function render() {
        var _this$props2 = this.props,
            forwardedRef = _this$props2.forwardedRef,
            propFallback = _this$props2.fallback,
            __chunkExtractor = _this$props2.__chunkExtractor,
            props = _objectWithoutPropertiesLoose(_this$props2, ["forwardedRef", "fallback", "__chunkExtractor"]);

        var _this$state = this.state,
            error = _this$state.error,
            loading = _this$state.loading,
            result = _this$state.result;

        if (options.suspense) {
          var cachedPromise = this.getCache() || this.loadAsync();

          if (cachedPromise.status === STATUS_PENDING) {
            throw this.loadAsync();
          }
        }

        if (error) {
          throw error;
        }

        var fallback = propFallback || options.fallback || null;

        if (loading) {
          return fallback;
        }

        return _render({
          fallback: fallback,
          result: result,
          options: options,
          props: (0,esm_extends/* default */.Z)({}, props, {
            ref: forwardedRef
          })
        });
      };

      return InnerLoadable;
    }(react.Component);

    var EnhancedInnerLoadable = withChunkExtractor(InnerLoadable);
    var Loadable = react.forwardRef(function (props, ref) {
      return react.createElement(EnhancedInnerLoadable, Object.assign({
        forwardedRef: ref
      }, props));
    });
    Loadable.displayName = 'Loadable'; // In future, preload could use `<link rel="preload">`

    Loadable.preload = function (props) {
      Loadable.load(props);
    };

    Loadable.load = function (props) {
      return cachedLoad(props);
    };

    return Loadable;
  }

  function lazy(ctor, options) {
    return loadable(ctor, (0,esm_extends/* default */.Z)({}, options, {
      suspense: true
    }));
  }

  return {
    loadable: loadable,
    lazy: lazy
  };
}

function defaultResolveComponent(loadedModule) {
  // eslint-disable-next-line no-underscore-dangle
  return loadedModule.__esModule ? loadedModule["default"] : loadedModule["default"] || loadedModule;
}

/* eslint-disable no-use-before-define, react/no-multi-comp */

var _createLoadable =
/*#__PURE__*/
createLoadable({
  defaultResolveComponent: defaultResolveComponent,
  render: function render(_ref) {
    var Component = _ref.result,
        props = _ref.props;
    return react.createElement(Component, props);
  }
}),
    loadable = _createLoadable.loadable,
    lazy = _createLoadable.lazy;

/* eslint-disable no-use-before-define, react/no-multi-comp */

var _createLoadable$1 =
/*#__PURE__*/
createLoadable({
  onLoad: function onLoad(result, props) {
    if (result && props.forwardedRef) {
      if (typeof props.forwardedRef === 'function') {
        props.forwardedRef(result);
      } else {
        props.forwardedRef.current = result;
      }
    }
  },
  render: function render(_ref) {
    var result = _ref.result,
        props = _ref.props;

    if (props.children) {
      return props.children(result);
    }

    return null;
  }
}),
    loadable$1 = _createLoadable$1.loadable,
    lazy$1 = _createLoadable$1.lazy;

/* eslint-disable no-underscore-dangle, camelcase */
var BROWSER = typeof window !== 'undefined';
function loadableReady(done, _temp) {
  if (done === void 0) {
    done = function done() {};
  }

  var _ref = _temp === void 0 ? {} : _temp,
      _ref$namespace = _ref.namespace,
      namespace = _ref$namespace === void 0 ? '' : _ref$namespace,
      _ref$chunkLoadingGlob = _ref.chunkLoadingGlobal,
      chunkLoadingGlobal = _ref$chunkLoadingGlob === void 0 ? '__LOADABLE_LOADED_CHUNKS__' : _ref$chunkLoadingGlob;

  if (!BROWSER) {
    warn('`loadableReady()` must be called in browser only');
    done();
    return Promise.resolve();
  }

  var requiredChunks = null;

  if (BROWSER) {
    var id = getRequiredChunkKey(namespace);
    var dataElement = document.getElementById(id);

    if (dataElement) {
      requiredChunks = JSON.parse(dataElement.textContent);
      var extElement = document.getElementById(id + "_ext");

      if (extElement) {
        var _JSON$parse = JSON.parse(extElement.textContent),
            namedChunks = _JSON$parse.namedChunks;

        namedChunks.forEach(function (chunkName) {
          LOADABLE_SHARED.initialChunks[chunkName] = true;
        });
      } else {
        // version mismatch
        throw new Error('loadable-component: @loadable/server does not match @loadable/component');
      }
    }
  }

  if (!requiredChunks) {
    warn('`loadableReady()` requires state, please use `getScriptTags` or `getScriptElements` server-side');
    done();
    return Promise.resolve();
  }

  var resolved = false;
  return new Promise(function (resolve) {
    window[chunkLoadingGlobal] = window[chunkLoadingGlobal] || [];
    var loadedChunks = window[chunkLoadingGlobal];
    var originalPush = loadedChunks.push.bind(loadedChunks);

    function checkReadyState() {
      if (requiredChunks.every(function (chunk) {
        return loadedChunks.some(function (_ref2) {
          var chunks = _ref2[0];
          return chunks.indexOf(chunk) > -1;
        });
      })) {
        if (!resolved) {
          resolved = true;
          resolve();
        }
      }
    }

    loadedChunks.push = function () {
      originalPush.apply(void 0, arguments);
      checkReadyState();
    };

    checkReadyState();
  }).then(done);
}

/* eslint-disable no-underscore-dangle */
var loadable$2 = loadable;
loadable$2.lib = loadable$1;
var lazy$2 = lazy;
lazy$2.lib = lazy$1;
var __SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = sharedInternals;

/* harmony default export */ const loadable_esm = (loadable$2);



/***/ }),

/***/ 2266:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

// THIS FILE IS AUTO GENERATED
var GenIcon = (__webpack_require__(9720)/* .GenIcon */ .w_)
module.exports.AiFillFolderAdd = function AiFillFolderAdd (props) {
  return GenIcon({"tag":"svg","attr":{"viewBox":"0 0 1024 1024"},"child":[{"tag":"path","attr":{"d":"M880 298.4H521L403.7 186.2a8.15 8.15 0 0 0-5.5-2.2H144c-17.7 0-32 14.3-32 32v592c0 17.7 14.3 32 32 32h736c17.7 0 32-14.3 32-32V330.4c0-17.7-14.3-32-32-32zM632 577c0 3.8-3.4 7-7.5 7H540v84.9c0 3.9-3.2 7.1-7 7.1h-42c-3.8 0-7-3.2-7-7.1V584h-84.5c-4.1 0-7.5-3.2-7.5-7v-42c0-3.8 3.4-7 7.5-7H484v-84.9c0-3.9 3.2-7.1 7-7.1h42c3.8 0 7 3.2 7 7.1V528h84.5c4.1 0 7.5 3.2 7.5 7v42z"}}]})(props);
};


/***/ }),

/***/ 5296:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

// THIS FILE IS AUTO GENERATED
var GenIcon = (__webpack_require__(9720)/* .GenIcon */ .w_)
module.exports.BsQuestion = function BsQuestion (props) {
  return GenIcon({"tag":"svg","attr":{"viewBox":"0 0 16 16","fill":"currentColor"},"child":[{"tag":"path","attr":{"d":"M5.25 6.033h1.32c0-.781.458-1.384 1.36-1.384.685 0 1.313.343 1.313 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.007.463h1.307v-.355c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.326 0-2.786.647-2.754 2.533zm1.562 5.516c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"}}]})(props);
};


/***/ }),

/***/ 4076:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

// THIS FILE IS AUTO GENERATED
var GenIcon = (__webpack_require__(9720)/* .GenIcon */ .w_)
module.exports.FaNewspaper = function FaNewspaper (props) {
  return GenIcon({"tag":"svg","attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M552 64H88c-13.255 0-24 10.745-24 24v8H24c-13.255 0-24 10.745-24 24v272c0 30.928 25.072 56 56 56h472c26.51 0 48-21.49 48-48V88c0-13.255-10.745-24-24-24zM56 400a8 8 0 0 1-8-8V144h16v248a8 8 0 0 1-8 8zm236-16H140c-6.627 0-12-5.373-12-12v-8c0-6.627 5.373-12 12-12h152c6.627 0 12 5.373 12 12v8c0 6.627-5.373 12-12 12zm208 0H348c-6.627 0-12-5.373-12-12v-8c0-6.627 5.373-12 12-12h152c6.627 0 12 5.373 12 12v8c0 6.627-5.373 12-12 12zm-208-96H140c-6.627 0-12-5.373-12-12v-8c0-6.627 5.373-12 12-12h152c6.627 0 12 5.373 12 12v8c0 6.627-5.373 12-12 12zm208 0H348c-6.627 0-12-5.373-12-12v-8c0-6.627 5.373-12 12-12h152c6.627 0 12 5.373 12 12v8c0 6.627-5.373 12-12 12zm0-96H140c-6.627 0-12-5.373-12-12v-40c0-6.627 5.373-12 12-12h360c6.627 0 12 5.373 12 12v40c0 6.627-5.373 12-12 12z"}}]})(props);
};


/***/ }),

/***/ 2659:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

// THIS FILE IS AUTO GENERATED
var GenIcon = (__webpack_require__(9720)/* .GenIcon */ .w_)
module.exports.ImCross = function ImCross (props) {
  return GenIcon({"tag":"svg","attr":{"version":"1.1","viewBox":"0 0 16 16"},"child":[{"tag":"path","attr":{"d":"M15.854 12.854c-0-0-0-0-0-0l-4.854-4.854 4.854-4.854c0-0 0-0 0-0 0.052-0.052 0.090-0.113 0.114-0.178 0.066-0.178 0.028-0.386-0.114-0.529l-2.293-2.293c-0.143-0.143-0.351-0.181-0.529-0.114-0.065 0.024-0.126 0.062-0.178 0.114 0 0-0 0-0 0l-4.854 4.854-4.854-4.854c-0-0-0-0-0-0-0.052-0.052-0.113-0.090-0.178-0.114-0.178-0.066-0.386-0.029-0.529 0.114l-2.293 2.293c-0.143 0.143-0.181 0.351-0.114 0.529 0.024 0.065 0.062 0.126 0.114 0.178 0 0 0 0 0 0l4.854 4.854-4.854 4.854c-0 0-0 0-0 0-0.052 0.052-0.090 0.113-0.114 0.178-0.066 0.178-0.029 0.386 0.114 0.529l2.293 2.293c0.143 0.143 0.351 0.181 0.529 0.114 0.065-0.024 0.126-0.062 0.178-0.114 0-0 0-0 0-0l4.854-4.854 4.854 4.854c0 0 0 0 0 0 0.052 0.052 0.113 0.090 0.178 0.114 0.178 0.066 0.386 0.029 0.529-0.114l2.293-2.293c0.143-0.143 0.181-0.351 0.114-0.529-0.024-0.065-0.062-0.126-0.114-0.178z"}}]})(props);
};


/***/ }),

/***/ 1140:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

// THIS FILE IS AUTO GENERATED
var GenIcon = (__webpack_require__(9720)/* .GenIcon */ .w_)
module.exports.IoMdSend = function IoMdSend (props) {
  return GenIcon({"tag":"svg","attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M48 448l416-192L48 64v149.333L346 256 48 298.667z"}}]})(props);
};


/***/ }),

/***/ 8679:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

"use strict";


var reactIs = __webpack_require__(9864);

/**
 * Copyright 2015, Yahoo! Inc.
 * Copyrights licensed under the New BSD License. See the accompanying LICENSE file for terms.
 */
var REACT_STATICS = {
  childContextTypes: true,
  contextType: true,
  contextTypes: true,
  defaultProps: true,
  displayName: true,
  getDefaultProps: true,
  getDerivedStateFromError: true,
  getDerivedStateFromProps: true,
  mixins: true,
  propTypes: true,
  type: true
};
var KNOWN_STATICS = {
  name: true,
  length: true,
  prototype: true,
  caller: true,
  callee: true,
  arguments: true,
  arity: true
};
var FORWARD_REF_STATICS = {
  '$$typeof': true,
  render: true,
  defaultProps: true,
  displayName: true,
  propTypes: true
};
var MEMO_STATICS = {
  '$$typeof': true,
  compare: true,
  defaultProps: true,
  displayName: true,
  propTypes: true,
  type: true
};
var TYPE_STATICS = {};
TYPE_STATICS[reactIs.ForwardRef] = FORWARD_REF_STATICS;
TYPE_STATICS[reactIs.Memo] = MEMO_STATICS;

function getStatics(component) {
  // React v16.11 and below
  if (reactIs.isMemo(component)) {
    return MEMO_STATICS;
  } // React v16.12 and above


  return TYPE_STATICS[component['$$typeof']] || REACT_STATICS;
}

var defineProperty = Object.defineProperty;
var getOwnPropertyNames = Object.getOwnPropertyNames;
var getOwnPropertySymbols = Object.getOwnPropertySymbols;
var getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
var getPrototypeOf = Object.getPrototypeOf;
var objectPrototype = Object.prototype;
function hoistNonReactStatics(targetComponent, sourceComponent, blacklist) {
  if (typeof sourceComponent !== 'string') {
    // don't hoist over string (html) components
    if (objectPrototype) {
      var inheritedComponent = getPrototypeOf(sourceComponent);

      if (inheritedComponent && inheritedComponent !== objectPrototype) {
        hoistNonReactStatics(targetComponent, inheritedComponent, blacklist);
      }
    }

    var keys = getOwnPropertyNames(sourceComponent);

    if (getOwnPropertySymbols) {
      keys = keys.concat(getOwnPropertySymbols(sourceComponent));
    }

    var targetStatics = getStatics(targetComponent);
    var sourceStatics = getStatics(sourceComponent);

    for (var i = 0; i < keys.length; ++i) {
      var key = keys[i];

      if (!KNOWN_STATICS[key] && !(blacklist && blacklist[key]) && !(sourceStatics && sourceStatics[key]) && !(targetStatics && targetStatics[key])) {
        var descriptor = getOwnPropertyDescriptor(sourceComponent, key);

        try {
          // Avoid failures from read-only properties
          defineProperty(targetComponent, key, descriptor);
        } catch (e) {}
      }
    }
  }

  return targetComponent;
}

module.exports = hoistNonReactStatics;


/***/ }),

/***/ 198:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ 2118:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ 7943:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ 6372:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ 537:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ 745:
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";


var m = __webpack_require__(3935);
if (true) {
  exports.createRoot = m.createRoot;
  exports.hydrateRoot = m.hydrateRoot;
} else { var i; }


/***/ }),

/***/ 9921:
/***/ ((__unused_webpack_module, exports) => {

"use strict";
/** @license React v16.13.1
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var b="function"===typeof Symbol&&Symbol.for,c=b?Symbol.for("react.element"):60103,d=b?Symbol.for("react.portal"):60106,e=b?Symbol.for("react.fragment"):60107,f=b?Symbol.for("react.strict_mode"):60108,g=b?Symbol.for("react.profiler"):60114,h=b?Symbol.for("react.provider"):60109,k=b?Symbol.for("react.context"):60110,l=b?Symbol.for("react.async_mode"):60111,m=b?Symbol.for("react.concurrent_mode"):60111,n=b?Symbol.for("react.forward_ref"):60112,p=b?Symbol.for("react.suspense"):60113,q=b?
Symbol.for("react.suspense_list"):60120,r=b?Symbol.for("react.memo"):60115,t=b?Symbol.for("react.lazy"):60116,v=b?Symbol.for("react.block"):60121,w=b?Symbol.for("react.fundamental"):60117,x=b?Symbol.for("react.responder"):60118,y=b?Symbol.for("react.scope"):60119;
function z(a){if("object"===typeof a&&null!==a){var u=a.$$typeof;switch(u){case c:switch(a=a.type,a){case l:case m:case e:case g:case f:case p:return a;default:switch(a=a&&a.$$typeof,a){case k:case n:case t:case r:case h:return a;default:return u}}case d:return u}}}function A(a){return z(a)===m}exports.AsyncMode=l;exports.ConcurrentMode=m;exports.ContextConsumer=k;exports.ContextProvider=h;exports.Element=c;exports.ForwardRef=n;exports.Fragment=e;exports.Lazy=t;exports.Memo=r;exports.Portal=d;
exports.Profiler=g;exports.StrictMode=f;exports.Suspense=p;exports.isAsyncMode=function(a){return A(a)||z(a)===l};exports.isConcurrentMode=A;exports.isContextConsumer=function(a){return z(a)===k};exports.isContextProvider=function(a){return z(a)===h};exports.isElement=function(a){return"object"===typeof a&&null!==a&&a.$$typeof===c};exports.isForwardRef=function(a){return z(a)===n};exports.isFragment=function(a){return z(a)===e};exports.isLazy=function(a){return z(a)===t};
exports.isMemo=function(a){return z(a)===r};exports.isPortal=function(a){return z(a)===d};exports.isProfiler=function(a){return z(a)===g};exports.isStrictMode=function(a){return z(a)===f};exports.isSuspense=function(a){return z(a)===p};
exports.isValidElementType=function(a){return"string"===typeof a||"function"===typeof a||a===e||a===m||a===g||a===f||a===p||a===q||"object"===typeof a&&null!==a&&(a.$$typeof===t||a.$$typeof===r||a.$$typeof===h||a.$$typeof===k||a.$$typeof===n||a.$$typeof===w||a.$$typeof===x||a.$$typeof===y||a.$$typeof===v)};exports.typeOf=z;


/***/ }),

/***/ 9864:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

"use strict";


if (true) {
  module.exports = __webpack_require__(9921);
} else {}


/***/ }),

/***/ 1002:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
var react_1 = __importDefault(__webpack_require__(7294));
var component_1 = __importDefault(__webpack_require__(2584));
var react_router_dom_1 = __webpack_require__(6068);
var components_1 = __webpack_require__(5520);
__webpack_require__(537);
var Dashboard = (0, component_1.default)(function () { return Promise.resolve().then(function () { return __importStar(__webpack_require__(3766)); }); });
var BraceForm = (0, component_1.default)(function () { return Promise.resolve().then(function () { return __importStar(__webpack_require__(5830)); }); });
var BraceList = (0, component_1.default)(function () { return Promise.resolve().then(function () { return __importStar(__webpack_require__(8368)); }); });
var Login = (0, component_1.default)(function () { return Promise.resolve().then(function () { return __importStar(__webpack_require__(8085)); }); });
var App = function () {
    return (react_1.default.createElement(react_router_dom_1.Routes, null,
        react_1.default.createElement(react_router_dom_1.Route, { path: 'login', element: react_1.default.createElement(Login, null) }),
        react_1.default.createElement(react_router_dom_1.Route, { path: '', element: react_1.default.createElement(Dashboard, null) },
            react_1.default.createElement(react_router_dom_1.Route, { index: true, element: react_1.default.createElement(BraceText, { text: 'Select a Model' }) }),
            react_1.default.createElement(react_router_dom_1.Route, { path: ':app_label/:model_name' },
                react_1.default.createElement(react_router_dom_1.Route, { path: '', element: react_1.default.createElement(BraceList, null) }),
                react_1.default.createElement(react_router_dom_1.Route, { path: 'add', element: react_1.default.createElement(BraceForm, null) }),
                react_1.default.createElement(react_router_dom_1.Route, { path: 'change/:pk', element: react_1.default.createElement(BraceForm, null) })),
            react_1.default.createElement(react_router_dom_1.Route, { path: '*', element: react_1.default.createElement(BraceText, { text: 'Not Found' }) }))));
};
var BraceText = function (_a) {
    var text = _a.text;
    return (react_1.default.createElement("div", { className: 'brace-text' },
        react_1.default.createElement(components_1.BouncyText, { text: text })));
};
exports["default"] = App;


/***/ }),

/***/ 6802:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.Footer = void 0;
var react_1 = __importDefault(__webpack_require__(7294));
var react_router_dom_1 = __webpack_require__(6068);
var jotai_1 = __webpack_require__(1131);
var state_1 = __webpack_require__(466);
var comps_1 = __webpack_require__(5520);
__webpack_require__(198);
var Footer = function () {
    var SubmitData = (0, jotai_1.useAtomValue)(state_1.BFSData);
    var navigate = (0, react_router_dom_1.useNavigate)();
    var _a = (0, react_router_dom_1.useParams)(), app_label = _a.app_label, model_name = _a.model_name, pk = _a.pk;
    var _b = __read((0, jotai_1.useAtom)(state_1.BFErrorsAtom), 2), BFErrors = _b[0], UpdateBFErrors = _b[1];
    var UpdateForm = (0, jotai_1.useSetAtom)(state_1.BraceFormAtom);
    var Submit = function () { return __awaiter(void 0, void 0, void 0, function () {
        var response;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4, (0, state_1.SubmitBraceForm)(SubmitData)];
                case 1:
                    response = _a.sent();
                    if (response.ok) {
                        (0, comps_1.ShowParticles)();
                        if (BFErrors)
                            UpdateBFErrors(null);
                        return [2, { ok: true, pk: response.pk }];
                    }
                    else {
                        UpdateBFErrors(response);
                        return [2, { ok: false }];
                    }
                    return [2];
            }
        });
    }); };
    var SaveAdd = function () { return __awaiter(void 0, void 0, void 0, function () {
        var ok;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4, Submit()];
                case 1:
                    ok = (_a.sent()).ok;
                    if (ok) {
                        if (pk)
                            navigate('../add');
                        else
                            location.reload();
                    }
                    return [2];
            }
        });
    }); };
    var SaveContinue = function () { return __awaiter(void 0, void 0, void 0, function () {
        var res;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4, Submit()];
                case 1:
                    res = _a.sent();
                    if (res.ok) {
                        if (pk)
                            UpdateForm({ app_label: app_label, model_name: model_name, pk: pk });
                        else
                            navigate("../change/".concat(res.pk));
                    }
                    return [2];
            }
        });
    }); };
    return (react_1.default.createElement("div", { className: 'footer title_small' },
        react_1.default.createElement("button", { style: { animationDelay: '0.5s' }, onClick: SaveAdd }, "Save and add another"),
        react_1.default.createElement("button", { style: { animationDelay: '1.5s' }, onClick: SaveContinue }, "Save and continue editing"),
        react_1.default.createElement("button", { style: { animationDelay: '1s' }, className: 'main', id: 'save-btn', onClick: function () { return Submit(); } }, "Save")));
};
exports.Footer = Footer;


/***/ }),

/***/ 5830:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
var react_1 = __importStar(__webpack_require__(7294));
var FaNewspaper_1 = __webpack_require__(4076);
var react_router_dom_1 = __webpack_require__(6068);
var jotai_1 = __webpack_require__(1131);
var state_1 = __webpack_require__(466);
var comps_1 = __webpack_require__(5520);
var Footer_1 = __webpack_require__(6802);
__webpack_require__(2118);
var BraceForm = function () {
    var _a = (0, react_router_dom_1.useParams)(), app_label = _a.app_label, model_name = _a.model_name, pk = _a.pk;
    var _b = __read((0, jotai_1.useAtom)(state_1.BraceFormAtom), 2), Form = _b[0], UpdateForm = _b[1];
    var _c = __read((0, jotai_1.useAtom)(state_1.BFSData), 2), UpdateSubmitData = _c[1];
    (0, react_1.useEffect)(function () {
        if (!app_label || !model_name)
            return;
        UpdateForm({ app_label: app_label, model_name: model_name, pk: pk });
        UpdateSubmitData({
            app_label: app_label,
            model_name: model_name,
            pk: pk,
            type: pk === undefined ? 'add' : 'change',
        });
    }, [app_label, model_name, pk]);
    if (Form === 'loading')
        return react_1.default.createElement(comps_1.Loading, null);
    return (react_1.default.createElement("div", { className: 'brace-form-container' },
        react_1.default.createElement(FormTitle, null),
        react_1.default.createElement("div", { className: 'form-data' }, Form.fieldsets.map(function (fieldset, index) { return (react_1.default.createElement(Fieldset, { fieldset: fieldset, key: index })); })),
        react_1.default.createElement(Footer_1.Footer, null)));
};
var FormTitle = function () {
    var _a = (0, react_router_dom_1.useParams)(), model_name = _a.model_name, pk = _a.pk;
    var _b = __read((0, jotai_1.useAtom)(state_1.BraceFormAtom), 1), Form = _b[0];
    var title = function () {
        if (pk === undefined)
            return "Add ".concat(model_name);
        if (Form === 'loading')
            return "Change ".concat(pk);
        return "Change ".concat(Form.label);
    };
    return (react_1.default.createElement("div", { className: 'form-title title' },
        react_1.default.createElement("span", null,
            react_1.default.createElement("div", { className: 'icon' },
                react_1.default.createElement(FaNewspaper_1.FaNewspaper, { size: 30 })),
            react_1.default.createElement("div", { className: 'holder' }, title()),
            react_1.default.createElement("div", { className: 'icon' },
                react_1.default.createElement(FaNewspaper_1.FaNewspaper, { size: 30 })))));
};
var Fieldset = function (_a) {
    var fieldset = _a.fieldset;
    return (react_1.default.createElement("div", { className: 'fieldset' },
        react_1.default.createElement(comps_1.Intersect, { className: 'fieldset-header' },
            fieldset.name && (react_1.default.createElement("h2", { className: 'fieldset-title title' },
                react_1.default.createElement("div", null, fieldset.name))),
            fieldset.description && (react_1.default.createElement("p", { className: 'fieldset-description title_small' }, fieldset.description))),
        fieldset.fields.map(function (field, index) { return (react_1.default.createElement(Field, { field: field, key: index })); })));
};
var Field = function (_a) {
    var field = _a.field;
    var Errors = (0, jotai_1.useAtomValue)(state_1.BFErrorsAtom);
    var error;
    if (Errors)
        error = Errors.fields[field.name];
    return (react_1.default.createElement(comps_1.Intersect, { className: 'fieldset-field' },
        error && react_1.default.createElement("span", { className: 'error' }, error),
        react_1.default.createElement("div", { className: 'data' },
            react_1.default.createElement("label", { className: 'label' }, field.label),
            react_1.default.createElement("div", { tabIndex: 1, className: 'result-input-wrapper' },
                react_1.default.createElement(comps_1.RenderField, { field: field, className: 'result-input description', style: {
                        transitionDelay: '0.5s',
                    } })))));
};
exports["default"] = BraceForm;


/***/ }),

/***/ 8934:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.BraceBody = void 0;
var react_1 = __importStar(__webpack_require__(7294));
var react_router_dom_1 = __webpack_require__(6068);
var jotai_1 = __webpack_require__(1131);
var state_1 = __webpack_require__(466);
var comps_1 = __webpack_require__(5520);
var LastIndexAtom = (0, jotai_1.atom)(null);
var BraceBody = function () {
    var BraceResult = (0, jotai_1.useAtomValue)(state_1.BraceResultAtom);
    var UpdateLastIndex = (0, jotai_1.useSetAtom)(LastIndexAtom);
    var Selecteds = (0, jotai_1.useAtomValue)(state_1.BraceSelectAtom);
    (0, react_1.useEffect)(function () {
        if (Selecteds.length === 0)
            UpdateLastIndex(null);
    }, [Selecteds]);
    if (BraceResult === 'loading')
        return react_1.default.createElement(react_1.default.Fragment, null);
    return (react_1.default.createElement("tbody", null, BraceResult.results.map(function (item, index) { return (react_1.default.createElement(Result, { key: index, index: index, result: item })); })));
};
exports.BraceBody = BraceBody;
var Result = function (_a) {
    var result = _a.result, index = _a.index;
    var pk = result[0];
    var _b = __read((0, jotai_1.useAtom)(state_1.BraceSelectAtom), 2), Selecteds = _b[0], UpdateSelecteds = _b[1];
    var _c = __read((0, jotai_1.useAtom)(LastIndexAtom), 2), LastIndex = _c[0], UpdateLastIndex = _c[1];
    var PKMap = (0, jotai_1.useAtomValue)(state_1.PKMapAtom);
    return (react_1.default.createElement("tr", null,
        react_1.default.createElement("td", { className: 'checkbox' },
            react_1.default.createElement("span", null,
                react_1.default.createElement("input", { type: 'checkbox', checked: Selecteds === 'all' || Selecteds.indexOf(pk) !== -1, onChange: function (e) {
                        var checked = e.currentTarget.checked;
                        UpdateSelecteds({
                            type: checked ? 'add' : 'remove',
                            id: pk,
                        });
                    }, onClick: function (e) {
                        if (PKMap === 'loading')
                            return;
                        var checked = e.currentTarget.checked;
                        var update_type = checked ? 'add' : 'remove';
                        if (checked)
                            UpdateLastIndex(index);
                        if (LastIndex === null || !e.shiftKey)
                            return;
                        var list;
                        if (LastIndex > index)
                            list = range(index, LastIndex);
                        else
                            list = range(LastIndex, index);
                        list.forEach(function (item) {
                            var item_pk = PKMap[item];
                            if (!item_pk)
                                return;
                            UpdateSelecteds({
                                type: update_type,
                                id: item_pk,
                            });
                        });
                    } }))),
        result.slice(1).map(function (field, index) { return (react_1.default.createElement("td", { key: index }, index === 0 ? (react_1.default.createElement(react_router_dom_1.Link, { to: "change/".concat(pk, "/") },
            react_1.default.createElement(comps_1.RenderValue, { v: field }))) : (react_1.default.createElement(comps_1.RenderValue, { v: field })))); })));
};
var range = function (min, max) {
    return Array.from(Array(max - min + 1), function (_, i) { return min + i; });
};


/***/ }),

/***/ 3434:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.BraceHead = void 0;
var react_1 = __importDefault(__webpack_require__(7294));
var jotai_1 = __webpack_require__(1131);
var state_1 = __webpack_require__(466);
var BraceHead = function (_a) {
    var results_length = _a.results_length, headers = _a.headers;
    var _b = __read((0, jotai_1.useAtom)(state_1.BraceSelectAtom), 2), Selecteds = _b[0], UpdateSelecteds = _b[1];
    var checked = function () {
        return Selecteds === 'all' ||
            (Selecteds.length === results_length && Selecteds.length > 0);
    };
    return (react_1.default.createElement("thead", null,
        react_1.default.createElement("tr", { className: 'title_small' },
            react_1.default.createElement("th", { className: 'checkbox' },
                react_1.default.createElement("span", null,
                    react_1.default.createElement("input", { type: 'checkbox', checked: checked(), onChange: function (e) {
                            var checked = e.currentTarget.checked;
                            UpdateSelecteds({
                                type: checked ? 'add' : 'remove',
                                id: 'page',
                            });
                        } }))),
            headers.map(function (head, index) { return (react_1.default.createElement("th", { key: index }, head)); }))));
};
exports.BraceHead = BraceHead;


/***/ }),

/***/ 2911:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
var react_1 = __importStar(__webpack_require__(7294));
var utils_1 = __webpack_require__(5071);
var BsQuestion_1 = __webpack_require__(5296);
var ImCross_1 = __webpack_require__(2659);
var IoMdSend_1 = __webpack_require__(1140);
var jotai_1 = __webpack_require__(1131);
var state_1 = __webpack_require__(466);
__webpack_require__(6372);
var Paginator = function (props) {
    var UpdateResultOptions = (0, jotai_1.useSetAtom)(state_1.ResultOptionsAtom);
    var _a = __read((0, react_1.useState)({
        page: 0,
        status: false,
    }), 2), SendPage = _a[0], setSendPage = _a[1];
    var _b = __read((0, react_1.useState)(false), 2), IsActive = _b[0], setIsActive = _b[1];
    var PageNumber = function (value) {
        if (!value)
            return;
        var page = parseInt(value);
        if (page > 0 && page <= props.max && page !== props.current) {
            return setSendPage({
                page: page,
                status: true,
            });
        }
        else {
            return setSendPage({
                page: 0,
                status: false,
            });
        }
    };
    return (react_1.default.createElement("div", { className: 'paginator-container' },
        react_1.default.createElement("ul", { className: 'paginator-items ' }, PageRange(props).map(function (item, index) {
            if (item === 'ep')
                return (react_1.default.createElement("li", { key: index, className: 'paginator-item description' },
                    react_1.default.createElement("span", { className: 'paginator-link' },
                        react_1.default.createElement("button", { className: 'paginator-link' }, "..."))));
            return (react_1.default.createElement("li", { key: index, className: 'paginator-item description' },
                react_1.default.createElement("button", { style: props.current === item
                        ? {
                            background: 'red',
                            opacity: 0.5,
                            cursor: 'not-allowed',
                        }
                        : {}, onClick: function () {
                        return props.current !== item &&
                            UpdateResultOptions({
                                page: item,
                            });
                    }, className: 'paginator-link paginator-link-number' }, item)));
        })),
        props.max > 5 && (react_1.default.createElement("div", { className: 'goto-container' + (0, utils_1.C)(IsActive) },
            react_1.default.createElement("input", { type: 'number', placeholder: 'Page Number...', autoFocus: IsActive, onChange: function (e) { return PageNumber(e.target.value); } }),
            react_1.default.createElement("button", { className: (0, utils_1.C)(SendPage.status), onClick: function () {
                    if (SendPage.status) {
                        UpdateResultOptions({
                            page: SendPage.page,
                        });
                    }
                    else {
                        setIsActive(!IsActive);
                    }
                } },
                react_1.default.createElement("div", { className: 'before' }, (0, utils_1.C)(IsActive) ? (react_1.default.createElement(ImCross_1.ImCross, { size: 18, fill: 'black' })) : (react_1.default.createElement(BsQuestion_1.BsQuestion, { size: 30, fill: 'black' }))),
                react_1.default.createElement("div", { className: 'after' },
                    react_1.default.createElement(IoMdSend_1.IoMdSend, { size: 28, fill: 'black' })))))));
};
var NumRange = function (start, end) {
    return Array.from(Array(end - start + 1)).map(function (_, idx) { return idx + start; });
};
var PageRange = function (_a) {
    var current = _a.current, max = _a.max;
    if (max <= 5)
        return NumRange(1, max);
    if (current <= 2)
        return [1, 2, 3, 'ep', max - 1, max];
    if (current >= max - 1)
        return [1, 'ep', max - 2, max - 1, max];
    return [1, 'ep', current - 1, current, current + 1, 'ep', max];
};
exports["default"] = Paginator;


/***/ }),

/***/ 8368:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
var react_1 = __importStar(__webpack_require__(7294));
var AiFillFolderAdd_1 = __webpack_require__(2266);
var react_router_dom_1 = __webpack_require__(6068);
var jotai_1 = __webpack_require__(1131);
var state_1 = __webpack_require__(466);
var comps_1 = __webpack_require__(5520);
var Body_1 = __webpack_require__(8934);
var Head_1 = __webpack_require__(3434);
var Paginator_1 = __importDefault(__webpack_require__(2911));
__webpack_require__(7943);
var Model_opts = [
    {
        lable: 'All',
        value: null,
    },
    {
        lable: 'Date (New-Old)',
        value: 'date',
    },
    {
        lable: 'Date (Old-New)',
        value: 'date_reverse',
    },
];
var BraceList = function () {
    var _a = (0, react_router_dom_1.useParams)(), app_label = _a.app_label, model_name = _a.model_name;
    var _b = __read((0, jotai_1.useAtom)(state_1.BraceInfoAtom), 2), BraceInfo = _b[0], UpdateBraceInfo = _b[1];
    var UpdateResultOptions = (0, jotai_1.useSetAtom)(state_1.ResultOptionsAtom);
    (0, react_1.useEffect)(function () {
        if (!app_label || !model_name)
            return;
        var app_model = "".concat(app_label, "/").concat(model_name);
        UpdateBraceInfo(app_model);
        UpdateResultOptions({ app_model: app_model });
    }, [app_label, model_name]);
    return (react_1.default.createElement("div", { className: 'brace-list' },
        react_1.default.createElement("div", { className: "header ".concat(BraceInfo !== 'loading' && BraceInfo.show_search
                ? ''
                : 'left') },
            BraceInfo !== 'loading' && BraceInfo.show_search && (react_1.default.createElement("div", { className: 'search-container' },
                react_1.default.createElement(comps_1.SearchInput, { submit: function (search) { return UpdateResultOptions({ search: search }); } }))),
            react_1.default.createElement("div", { className: 'options-wrapper title_smaller' },
                react_1.default.createElement(react_router_dom_1.Link, { to: 'add', className: 'add-container' },
                    react_1.default.createElement("div", { className: 'holder' },
                        "Add ",
                        react_1.default.createElement("span", { className: 'model_name' }, model_name)),
                    react_1.default.createElement("div", { className: 'icon' },
                        react_1.default.createElement(AiFillFolderAdd_1.AiFillFolderAdd, { size: 24 }))),
                react_1.default.createElement("div", { className: 'filter-container' },
                    react_1.default.createElement(comps_1.Select, { options: Model_opts, defaultOpt: Model_opts[0] })))),
        react_1.default.createElement(react_1.Suspense, null,
            react_1.default.createElement(Result, null))));
};
var Result = function () {
    var BraceInfo = (0, jotai_1.useAtomValue)(state_1.BraceInfoAtom);
    var ResultOptions = (0, jotai_1.useAtomValue)(state_1.ResultOptionsAtom);
    var _a = __read((0, jotai_1.useAtom)(state_1.BraceResultAtom), 2), BraceResult = _a[0], UpdateBraceResult = _a[1];
    (0, react_1.useEffect)(function () {
        UpdateBraceResult();
    }, [ResultOptions]);
    if (BraceInfo === 'loading')
        return react_1.default.createElement(comps_1.Loading, null);
    return (react_1.default.createElement(react_1.default.Fragment, null,
        react_1.default.createElement("div", { className: 'result' },
            react_1.default.createElement("table", null,
                react_1.default.createElement(Head_1.BraceHead, { headers: BraceInfo.headers, results_length: BraceResult === 'loading'
                        ? 0
                        : BraceResult.results.length }),
                BraceResult !== 'loading' && react_1.default.createElement(Body_1.BraceBody, null)),
            BraceResult === 'loading' && react_1.default.createElement(comps_1.Loading, null)),
        BraceResult !== 'loading' && BraceResult.page && (react_1.default.createElement(Paginator_1.default, __assign({}, BraceResult.page)))));
};
exports["default"] = BraceList;


/***/ }),

/***/ 4712:
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
var react_1 = __importDefault(__webpack_require__(7294));
var client_1 = __webpack_require__(745);
var react_router_dom_1 = __webpack_require__(6068);
var App_1 = __importDefault(__webpack_require__(1002));
var Root = function () {
    return (react_1.default.createElement(react_router_dom_1.BrowserRouter, { basename: BASE_URL },
        react_1.default.createElement(App_1.default, null)));
};
(0, client_1.createRoot)(document.getElementById('root')).render(react_1.default.createElement(Root, null));


/***/ })

},
/******/ __webpack_require__ => { // webpackRuntimeModules
/******/ var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
/******/ __webpack_require__.O(0, [438,362,222,160,712,394], () => (__webpack_exec__(4712)));
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=source_maps/main.0523ff13b6b0bc11bbc0.js.map