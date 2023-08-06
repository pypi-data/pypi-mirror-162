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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewerView = exports.ViewerModel = void 0;
const jupyter_dataserializers_1 = require("jupyter-dataserializers");
const ITKHelper_1 = __importDefault(require("vtk.js/Sources/Common/DataModel/ITKHelper"));
const Coordinate_1 = __importDefault(require("vtk.js/Sources/Rendering/Core/Coordinate"));
const vtk_1 = __importDefault(require("vtk.js/Sources/vtk"));
const Constants_1 = require("vtk.js/Sources/Common/Core/DataArray/Constants");
const createViewer_1 = __importDefault(require("itk-vtk-viewer/src/createViewer"));
const IntTypes_1 = __importDefault(require("itk/IntTypes"));
const FloatTypes_1 = __importDefault(require("itk/FloatTypes"));
const IOTypes_1 = __importDefault(require("itk/IOTypes"));
const runPipelineBrowser_1 = __importDefault(require("itk/runPipelineBrowser"));
const WorkerPool_1 = __importDefault(require("itk/WorkerPool"));
const macro_1 = __importDefault(require("vtk.js/Sources/macro"));
const base_1 = require("@jupyter-widgets/base");
const version_1 = require("./version");
const ANNOTATION_DEFAULT = '<table style="margin-left: 0;"><tr><td style="margin-left: auto; margin-right: 0;">Index:</td><td>${iIndex},</td><td>${jIndex},</td><td>${kIndex}</td></tr><tr><td style="margin-left: auto; margin-right: 0;">Position:</td><td>${xPosition},</td><td>${yPosition},</td><td>${zPosition}</td></tr><tr><td style="margin-left: auto; margin-right: 0;"">Value:</td><td style="text-align:center;" colspan="3">${value}</td></tr><tr ${annotationLabelStyle}><td style="margin-left: auto; margin-right: 0;">Label:</td><td style="text-align:center;" colspan="3">${annotation}</td></tr></table>';
const ANNOTATION_CUSTOM_PREFIX = '<table style="margin-left: 0;"><tr><td style="margin-left: auto; margin-right: 0;">Scale/Index:</td>';
const ANNOTATION_CUSTOM_POSTFIX = '</tr><tr><td style="margin-left: auto; margin-right: 0;">Position:</td><td>${xPosition},</td><td>${yPosition},</td><td>${zPosition}</td></tr><tr><td style="margin-left: auto; margin-right: 0;"">Value:</td><td style="text-align:center;" colspan="3">${value}</td></tr><tr ${annotationLabelStyle}><td style="margin-left: auto; margin-right: 0;">Label:</td><td style="text-align:center;" colspan="3">${annotation}</td></tr></table>';
const cores = navigator.hardwareConcurrency ? navigator.hardwareConcurrency : 4;
const numberOfWorkers = cores + Math.floor(Math.sqrt(cores));
const workerPool = new WorkerPool_1.default(numberOfWorkers, runPipelineBrowser_1.default);
const serialize_itkimage = (itkimage) => {
    if (itkimage === null) {
        return null;
    }
    else {
        itkimage.data = null;
        return itkimage;
    }
};
const deserialize_itkimage = (jsonitkimage) => {
    if (jsonitkimage === null) {
        return null;
    }
    else {
        return jsonitkimage;
    }
};
const serialize_polydata_list = (polydata_list) => {
    if (polydata_list === null) {
        return null;
    }
    else {
        polydata_list.data = null;
        return polydata_list;
    }
};
const deserialize_polydata_list = (jsonpolydata_list) => {
    if (jsonpolydata_list === null) {
        return null;
    }
    else {
        return jsonpolydata_list;
    }
};
const serialize_image_point = (data) => {
    if (data === null) {
        return null;
    }
    else {
        return {
            index: jupyter_dataserializers_1.simplearray_serialization.serialize({
                shape: [3],
                array: new Int32Array([data.iIndex, data.jIndex, data.kIndex])
            }),
            position: jupyter_dataserializers_1.simplearray_serialization.serialize({
                shape: [3],
                array: new Float64Array([
                    data.xPosition,
                    data.yPosition,
                    data.zPosition
                ])
            }),
            value: jupyter_dataserializers_1.simplearray_serialization.serialize({
                shape: [data.value.length],
                array: new Float64Array(data.value)
            }),
            label: data.label
        };
    }
};
const deserialize_image_point = (data) => {
    if (data === null) {
        return null;
    }
    else {
        return {
            iIndex: data.index[0],
            jIndex: data.index[1],
            kIndex: data.index[2],
            xPosition: data.position[0],
            yPosition: data.position[1],
            zPosition: data.position[2],
            value: Array.from(data.value),
            label: data.label
        };
    }
};
class ViewerModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: ViewerModel.model_name, _model_module: ViewerModel.model_module, _model_module_version: ViewerModel.model_module_version, _view_name: ViewerModel.view_name, _view_module: ViewerModel.view_module, _view_module_version: ViewerModel.view_module_version, rendered_image: null, rendered_label_image: null, label_image_names: null, label_image_weights: null, label_image_blend: 0.5, _rendering_image: false, interpolation: true, cmap: null, lut: 'glasbey', _custom_cmap: { array: new Float32Array([0, 0, 0]), shape: [1, 3] }, vmin: null, vmax: null, shadow: true, slicing_planes: false, x_slice: null, y_slice: null, z_slice: null, clicked_slice_point: null, gradient_opacity: 0.2, sample_distance: 0.25, opacity_gaussians: null, channels: null, blend_mode: 'composite', roi: new Float64Array([0, 0, 0, 0, 0, 0]), _largest_roi: new Float64Array([0, 0, 0, 0, 0, 0]), select_roi: false, _reset_crop_requested: false, _scale_factors: new Uint8Array([1, 1, 1]), units: '', point_sets: null, point_set_colors: { array: new Float32Array([0, 0, 0]), shape: [1, 3] }, point_set_opacities: { array: new Float32Array([1.0]), shape: [1] }, point_set_sizes: { array: new Uint8Array([3]), shape: [1] }, point_set_representations: new Array(), geometries: null, geometry_colors: new Float32Array([0, 0, 0]), geometry_opacities: new Float32Array([1.0]), ui_collapsed: false, rotate: false, annotations: true, axes: true, mode: 'v', camera: new Float32Array(9), background: null });
    }
}
exports.ViewerModel = ViewerModel;
ViewerModel.model_name = 'ViewerModel';
ViewerModel.model_module = version_1.MODULE_NAME;
ViewerModel.model_module_version = version_1.MODULE_VERSION;
ViewerModel.view_name = 'ViewerView'; // Set to null if no view
ViewerModel.view_module = version_1.MODULE_NAME; // Set to null if no view
ViewerModel.view_module_version = version_1.MODULE_VERSION;
ViewerModel.serializers = Object.assign(Object.assign({}, base_1.DOMWidgetModel.serializers), { rendered_image: {
        serialize: serialize_itkimage,
        deserialize: deserialize_itkimage
    }, rendered_label_image: {
        serialize: serialize_itkimage,
        deserialize: deserialize_itkimage
    }, label_image_weights: jupyter_dataserializers_1.simplearray_serialization, clicked_slice_point: {
        serialize: serialize_image_point,
        deserialize: deserialize_image_point
    }, _custom_cmap: jupyter_dataserializers_1.simplearray_serialization, point_sets: {
        serialize: serialize_polydata_list,
        deserialize: deserialize_polydata_list
    }, geometries: {
        serialize: serialize_polydata_list,
        deserialize: deserialize_polydata_list
    }, roi: jupyter_dataserializers_1.fixed_shape_serialization([2, 3]), _largest_roi: jupyter_dataserializers_1.fixed_shape_serialization([2, 3]), _scale_factors: jupyter_dataserializers_1.fixed_shape_serialization([3]), camera: jupyter_dataserializers_1.fixed_shape_serialization([3, 3]), point_set_colors: jupyter_dataserializers_1.simplearray_serialization, point_set_opacities: jupyter_dataserializers_1.simplearray_serialization, point_set_sizes: jupyter_dataserializers_1.simplearray_serialization, geometry_colors: jupyter_dataserializers_1.simplearray_serialization, geometry_opacities: jupyter_dataserializers_1.simplearray_serialization });
const createRenderingPipeline = (domWidgetView, { rendered_image, rendered_label_image, point_sets, geometries }) => {
    const containerStyle = {
        position: 'relative',
        width: '100%',
        height: '700px',
        minHeight: '400px',
        minWidth: '400px',
        margin: '1',
        padding: '1',
        top: '0',
        left: '0',
        overflow: 'hidden',
        display: 'block-inline'
    };
    let backgroundColor = [1.0, 1.0, 1.0];
    const bodyBackground = getComputedStyle(document.body).getPropertyValue('background-color');
    if (bodyBackground) {
        // Separator can be , or space
        const sep = bodyBackground.indexOf(',') > -1 ? ',' : ' ';
        // Turn "rgb(r,g,b)" into [r,g,b]
        const rgb = bodyBackground.substr(4).split(')')[0].split(sep);
        backgroundColor[0] = parseFloat(rgb[0]) / 255.0;
        backgroundColor[1] = parseFloat(rgb[1]) / 255.0;
        backgroundColor[2] = parseFloat(rgb[2]) / 255.0;
    }
    const backgroundTrait = domWidgetView.model.get('background');
    if (backgroundTrait.length !== 0) {
        backgroundColor = backgroundTrait;
    }
    const viewerStyle = {
        backgroundColor,
        containerStyle: containerStyle
    };
    let is3D = true;
    let imageData = null;
    let labelMapData = null;
    if (rendered_image) {
        imageData = ITKHelper_1.default.convertItkToVtkImage(rendered_image);
        is3D = rendered_image.imageType.dimension === 3;
    }
    if (rendered_label_image) {
        labelMapData = ITKHelper_1.default.convertItkToVtkImage(rendered_label_image);
        is3D = rendered_label_image.imageType.dimension === 3;
    }
    let pointSets = null;
    if (point_sets) {
        pointSets = point_sets.map((point_set) => vtk_1.default(point_set));
    }
    let vtkGeometries = null;
    if (geometries) {
        vtkGeometries = geometries.map((geometry) => vtk_1.default(geometry));
    }
    domWidgetView.use2D = !is3D;
    domWidgetView.skipOnCroppingPlanesChanged = false;
    domWidgetView.itkVtkViewer = createViewer_1.default(domWidgetView.el, {
        viewerStyle: viewerStyle,
        image: imageData,
        labelMap: labelMapData,
        pointSets,
        geometries: vtkGeometries,
        use2D: !is3D,
        rotate: false
    });
    const viewProxy = domWidgetView.itkVtkViewer.getViewProxy();
    const renderWindow = viewProxy.getRenderWindow();
    // Firefox requires calling .getContext on the canvas, which is
    // performed by .initialize()
    renderWindow.getViews()[0].initialize();
    const viewCanvas = renderWindow.getViews()[0].getCanvas();
    const stream = viewCanvas.captureStream(30000 / 1001);
    const renderer = viewProxy.getRenderer();
    const viewportPosition = Coordinate_1.default.newInstance();
    viewportPosition.setCoordinateSystemToNormalizedViewport();
    // Used by ipywebrtc
    domWidgetView.model.stream = Promise.resolve(stream);
    domWidgetView.initialize_viewer();
    const cropROIByViewport = (event) => {
        if (domWidgetView.model.get('select_roi')) {
            return;
        }
        let mode = domWidgetView.model.get('mode');
        if (mode === 'v') {
            if (domWidgetView.use2D) {
                mode = 'z';
            }
            else {
                return;
            }
        }
        viewportPosition.setValue(0.0, 0.0, 0.0);
        const lowerLeft = viewportPosition.getComputedWorldValue(renderer);
        viewportPosition.setValue(1.0, 1.0, 0.0);
        const upperRight = viewportPosition.getComputedWorldValue(renderer);
        const modelRoi = domWidgetView.model.get('roi');
        const roi = !!modelRoi.slice ? modelRoi : new Float32Array(modelRoi.buffer);
        const modelLargestRoi = domWidgetView.model.get('_largest_roi');
        const largestRoi = !!modelLargestRoi.slice ? modelLargestRoi : new Float32Array(modelLargestRoi.buffer);
        const padFactor = 0.5;
        const xPadding = (upperRight[0] - lowerLeft[0]) * padFactor;
        let yPadding = (upperRight[1] - lowerLeft[1]) * padFactor;
        if (mode === 'z') {
            yPadding = (lowerLeft[1] - upperRight[1]) * padFactor;
        }
        const zPadding = (upperRight[2] - lowerLeft[2]) * padFactor;
        switch (mode) {
            case 'x':
                roi[1] = lowerLeft[1] - yPadding;
                roi[4] = upperRight[1] + yPadding;
                roi[2] = lowerLeft[2] - zPadding;
                roi[5] = upperRight[2] + zPadding;
                // Zoom all the way out
                if (roi[2] < largestRoi[2] &&
                    roi[1] < largestRoi[1] &&
                    roi[5] > largestRoi[5] &&
                    roi[4] > largestRoi[4]) {
                    roi[2] = largestRoi[2];
                    roi[1] = largestRoi[1];
                    roi[5] = largestRoi[5];
                    roi[4] = largestRoi[4];
                    break;
                }
                break;
            case 'y':
                roi[0] = lowerLeft[0] - xPadding;
                roi[3] = upperRight[0] + xPadding;
                roi[2] = lowerLeft[2] - zPadding;
                roi[5] = upperRight[2] + zPadding;
                // Zoom all the way out
                if (roi[2] < largestRoi[2] &&
                    roi[0] < largestRoi[0] &&
                    roi[5] > largestRoi[5] &&
                    roi[3] > largestRoi[3]) {
                    roi[2] = largestRoi[2];
                    roi[0] = largestRoi[0];
                    roi[5] = largestRoi[5];
                    roi[3] = largestRoi[3];
                    break;
                }
                break;
            case 'z':
                roi[0] = lowerLeft[0] - xPadding;
                roi[3] = upperRight[0] + xPadding;
                roi[1] = upperRight[1] - yPadding;
                roi[4] = lowerLeft[1] + yPadding;
                // Zoom all the way out
                if (roi[0] < largestRoi[0] &&
                    roi[1] < largestRoi[1] &&
                    roi[3] > largestRoi[3] &&
                    roi[4] > largestRoi[4]) {
                    roi[0] = largestRoi[0];
                    roi[1] = largestRoi[1];
                    roi[3] = largestRoi[3];
                    roi[4] = largestRoi[4];
                    break;
                }
                break;
            default:
                throw new Error('Unexpected view mode');
        }
        domWidgetView.model.set('roi', roi);
        domWidgetView.model.save_changes();
    };
    if (rendered_image || rendered_label_image) {
        const interactor = viewProxy.getInteractor();
        interactor.onEndMouseWheel(cropROIByViewport);
        interactor.onEndPan(cropROIByViewport);
        interactor.onEndPinch(cropROIByViewport);
        if (rendered_image) {
            const imageData = ITKHelper_1.default.convertItkToVtkImage(rendered_image);
            const dataArray = imageData.getPointData().getScalars();
            const numberOfComponents = dataArray.getNumberOfComponents();
            if (domWidgetView.use2D &&
                dataArray.getDataType() === 'Uint8Array' &&
                (numberOfComponents === 3 || numberOfComponents === 4)) {
                domWidgetView.itkVtkViewer.setColorMap(0, 'Grayscale');
                domWidgetView.model.set('cmap', ['Grayscale']);
                domWidgetView.model.save_changes();
            }
        }
        domWidgetView.model.set('_rendering_image', false);
        domWidgetView.model.save_changes();
    }
};
function replaceRenderedImage(domWidgetView, rendered_image) {
    const imageData = ITKHelper_1.default.convertItkToVtkImage(rendered_image);
    domWidgetView.skipOnCroppingPlanesChanged = true;
    domWidgetView.itkVtkViewer.setImage(imageData);
    // Why is this necessary?
    const viewProxy = domWidgetView.itkVtkViewer.getViewProxy();
    const shadow = domWidgetView.model.get('shadow');
    const representation = viewProxy.getRepresentations()[0];
    representation.setUseShadow(shadow);
    // Todo: Fix this in vtk.js
    representation.setEdgeGradient(representation.getEdgeGradient() + 1e-7);
    if (viewProxy.getViewMode() === 'VolumeRendering') {
        viewProxy.resetCamera();
    }
    const dataArray = imageData.getPointData().getScalars();
    const numberOfComponents = dataArray.getNumberOfComponents();
    if (domWidgetView.use2D &&
        dataArray.getDataType() === 'Uint8Array' &&
        (numberOfComponents === 3 || numberOfComponents === 4)) {
        domWidgetView.itkVtkViewer.setColorMap(0, 'Grayscale');
        domWidgetView.model.set('cmap', ['Grayscale']);
        domWidgetView.model.save_changes();
    }
    domWidgetView.model.set('_rendering_image', false);
    domWidgetView.model.save_changes();
}
function replaceRenderedLabelMap(domWidgetView, rendered_label_image) {
    const labelMapData = ITKHelper_1.default.convertItkToVtkImage(rendered_label_image);
    domWidgetView.itkVtkViewer.setLabelMap(labelMapData);
    const viewProxy = domWidgetView.itkVtkViewer.getViewProxy();
    if (viewProxy.getViewMode() === 'VolumeRendering') {
        viewProxy.resetCamera();
    }
    domWidgetView.model.set('_rendering_image', false);
    domWidgetView.model.save_changes();
}
function replacePointSets(domWidgetView, pointSets) {
    const vtkPointSets = pointSets.map((pointSet) => vtk_1.default(pointSet));
    domWidgetView.itkVtkViewer.setPointSets(vtkPointSets);
    domWidgetView.point_set_colors_changed();
    domWidgetView.point_set_opacities_changed();
    domWidgetView.point_set_sizes_changed();
    domWidgetView.point_set_representations_changed();
    domWidgetView.itkVtkViewer.renderLater();
}
function replaceGeometries(domWidgetView, geometries) {
    const vtkGeometries = geometries.map((geometry) => vtk_1.default(geometry));
    domWidgetView.itkVtkViewer.setGeometries(vtkGeometries);
    domWidgetView.geometry_colors_changed();
    domWidgetView.geometry_opacities_changed();
    domWidgetView.itkVtkViewer.renderLater();
}
function decompressImage(image) {
    return __awaiter(this, void 0, void 0, function* () {
        if (image.data) {
            return image;
        }
        const byteArray = new Uint8Array(image.compressedData.buffer);
        const reducer = (accumulator, currentValue) => accumulator * currentValue;
        const pixelCount = image.size.reduce(reducer, 1);
        let componentSize = 0;
        switch (image.imageType.componentType) {
            case IntTypes_1.default.Int8:
                componentSize = 1;
                break;
            case IntTypes_1.default.UInt8:
                componentSize = 1;
                break;
            case IntTypes_1.default.Int16:
                componentSize = 2;
                break;
            case IntTypes_1.default.UInt16:
                componentSize = 2;
                break;
            case IntTypes_1.default.Int32:
                componentSize = 4;
                break;
            case IntTypes_1.default.UInt32:
                componentSize = 4;
                break;
            case IntTypes_1.default.Int64:
                componentSize = 8;
                break;
            case IntTypes_1.default.UInt64:
                componentSize = 8;
                break;
            case FloatTypes_1.default.Float32:
                componentSize = 4;
                break;
            case FloatTypes_1.default.Float64:
                componentSize = 8;
                break;
            default:
                console.error('Unexpected component type: ' + image.imageType.componentType);
        }
        const numberOfBytes = pixelCount * image.imageType.components * componentSize;
        const pipelinePath = 'ZstdDecompress';
        const args = ['input.bin', 'output.bin', String(numberOfBytes)];
        const desiredOutputs = [{ path: 'output.bin', type: IOTypes_1.default.Binary }];
        const inputs = [{ path: 'input.bin', type: IOTypes_1.default.Binary, data: byteArray }];
        console.log(`input MB: ${byteArray.length / 1000 / 1000}`);
        console.log(`output MB: ${numberOfBytes / 1000 / 1000}`);
        const compressionAmount = byteArray.length / numberOfBytes;
        console.log(`compression amount: ${compressionAmount}`);
        const t0 = performance.now();
        const taskArgsArray = [[pipelinePath, args, desiredOutputs, inputs]];
        const results = yield workerPool.runTasks(taskArgsArray);
        const t1 = performance.now();
        const duration = Number(t1 - t0)
            .toFixed(1)
            .toString();
        console.log('decompression took ' + duration + ' milliseconds.');
        const decompressed = results[0].outputs[0].data;
        switch (image.imageType.componentType) {
            case IntTypes_1.default.Int8:
                image.data = new Int8Array(decompressed.buffer);
                break;
            case IntTypes_1.default.UInt8:
                image.data = decompressed;
                break;
            case IntTypes_1.default.Int16:
                image.data = new Int16Array(decompressed.buffer);
                break;
            case IntTypes_1.default.UInt16:
                image.data = new Uint16Array(decompressed.buffer);
                break;
            case IntTypes_1.default.Int32:
                image.data = new Int32Array(decompressed.buffer);
                break;
            case IntTypes_1.default.UInt32:
                image.data = new Uint32Array(decompressed.buffer);
                break;
            case IntTypes_1.default.Int64:
                image.data = new BigUint64Array(decompressed.buffer);
                break;
            case IntTypes_1.default.UInt64:
                image.data = new BigUint64Array(decompressed.buffer);
                break;
            case FloatTypes_1.default.Float32:
                image.data = new Float32Array(decompressed.buffer);
                break;
            case FloatTypes_1.default.Float64:
                image.data = new Float64Array(decompressed.buffer);
                break;
            default:
                console.error('Unexpected component type: ' + image.imageType.componentType);
        }
        return image;
    });
}
// function decompressDataValue (polyData, prop) {
//   if (!polyData.hasOwnProperty(prop)) {
//     return Promise.resolve(polyData)
//   }
//   const byteArray = new Uint8Array(polyData[prop].compressedValues.buffer)
//   const elementSize = DataTypeByteSize[polyData[prop].dataType]
//   const numberOfBytes = polyData[prop].size * elementSize
//   const pipelinePath = 'ZstdDecompress'
//   const args = ['input.bin', 'output.bin', String(numberOfBytes)]
//   const desiredOutputs = [{ path: 'output.bin', type: IOTypes.Binary }]
//   const inputs = [{ path: 'input.bin', type: IOTypes.Binary, data: byteArray }]
//   console.log(`${prop} input MB: ${byteArray.length / 1000 / 1000}`)
//   console.log(`${prop} output MB: ${numberOfBytes / 1000 / 1000}`)
//   const compressionAmount = byteArray.length / numberOfBytes
//   console.log(`${prop} compression amount: ${compressionAmount}`)
//   const t0 = performance.now()
//   return runPipelineBrowser(
//     null,
//     pipelinePath,
//     args,
//     desiredOutputs,
//     inputs
//   ).then(function ({ stdout, stderr, outputs, webWorker }) {
//     webWorker.terminate()
//     const t1 = performance.now()
//     const duration = Number(t1 - t0)
//       .toFixed(1)
//       .toString()
//     console.log(`${prop} decompression took ${duration} milliseconds.`)
//     polyData[prop].values = new window[polyData[prop].dataType](
//       outputs[0].data.buffer
//     )
//     return polyData
//   })
// }
function decompressPolyData(polyData) {
    return __awaiter(this, void 0, void 0, function* () {
        const props = ['points', 'verts', 'lines', 'polys', 'strips'];
        const decompressedProps = [];
        const taskArgsArray = [];
        for (let index = 0; index < props.length; index++) {
            const prop = props[index];
            if (!polyData.hasOwnProperty(prop)) {
                continue;
            }
            const byteArray = new Uint8Array(polyData[prop].compressedValues.buffer);
            const elementSize = Constants_1.DataTypeByteSize[polyData[prop].dataType];
            const numberOfBytes = polyData[prop].size * elementSize;
            const pipelinePath = 'ZstdDecompress';
            const args = ['input.bin', 'output.bin', String(numberOfBytes)];
            const desiredOutputs = [{ path: 'output.bin', type: IOTypes_1.default.Binary }];
            const inputs = [
                { path: 'input.bin', type: IOTypes_1.default.Binary, data: byteArray }
            ];
            console.log(`${prop} input MB: ${byteArray.length / 1000 / 1000}`);
            console.log(`${prop} output MB: ${numberOfBytes / 1000 / 1000}`);
            const compressionAmount = byteArray.length / numberOfBytes;
            console.log(`${prop} compression amount: ${compressionAmount}`);
            taskArgsArray.push([pipelinePath, args, desiredOutputs, inputs]);
            decompressedProps.push(prop);
        }
        const decompressedPointData = [];
        if (polyData.hasOwnProperty('pointData')) {
            const pointDataArrays = polyData.pointData.arrays;
            for (let index = 0; index < pointDataArrays.length; index++) {
                const array = pointDataArrays[index];
                const byteArray = new Uint8Array(array.data.compressedValues.buffer);
                const elementSize = Constants_1.DataTypeByteSize[array.data.dataType];
                const numberOfBytes = array.data.size * elementSize;
                const pipelinePath = 'ZstdDecompress';
                const args = ['input.bin', 'output.bin', String(numberOfBytes)];
                const desiredOutputs = [{ path: 'output.bin', type: IOTypes_1.default.Binary }];
                const inputs = [
                    { path: 'input.bin', type: IOTypes_1.default.Binary, data: byteArray }
                ];
                console.log(`${array} input MB: ${byteArray.length / 1000 / 1000}`);
                console.log(`${array} output MB: ${numberOfBytes / 1000 / 1000}`);
                const compressionAmount = byteArray.length / numberOfBytes;
                console.log(`${array} compression amount: ${compressionAmount}`);
                taskArgsArray.push([pipelinePath, args, desiredOutputs, inputs]);
                decompressedPointData.push(array);
            }
        }
        const decompressedCellData = [];
        if (polyData.hasOwnProperty('cellData')) {
            const cellDataArrays = polyData.cellData.arrays;
            for (let index = 0; index < cellDataArrays.length; index++) {
                const array = cellDataArrays[index];
                const byteArray = new Uint8Array(array.data.compressedValues.buffer);
                const elementSize = Constants_1.DataTypeByteSize[array.data.dataType];
                const numberOfBytes = array.data.size * elementSize;
                const pipelinePath = 'ZstdDecompress';
                const args = ['input.bin', 'output.bin', String(numberOfBytes)];
                const desiredOutputs = [{ path: 'output.bin', type: IOTypes_1.default.Binary }];
                const inputs = [
                    { path: 'input.bin', type: IOTypes_1.default.Binary, data: byteArray }
                ];
                console.log(`${array} input MB: ${byteArray.length / 1000 / 1000}`);
                console.log(`${array} output MB: ${numberOfBytes / 1000 / 1000}`);
                const compressionAmount = byteArray.length / numberOfBytes;
                console.log(`${array} compression amount: ${compressionAmount}`);
                taskArgsArray.push([pipelinePath, args, desiredOutputs, inputs]);
                decompressedCellData.push(array);
            }
        }
        const t0 = performance.now();
        const results = yield workerPool.runTasks(taskArgsArray);
        const t1 = performance.now();
        const duration = Number(t1 - t0)
            .toFixed(1)
            .toString();
        console.log(`PolyData decompression took ${duration} milliseconds.`);
        for (let index = 0; index < decompressedProps.length; index++) {
            const prop = decompressedProps[index];
            // @ts-ignore: TS2351: This expression is not constructable.
            polyData[prop].values = new window[polyData[prop].dataType](results[index].outputs[0].data.buffer);
        }
        for (let index = 0; index < decompressedPointData.length; index++) {
            // @ts-ignore: TS2351: This expression is not constructable.
            polyData.pointData.arrays[index].data.values = new window[polyData.pointData.arrays[index].data.dataType](results[decompressedProps.length + index].outputs[0].data.buffer);
        }
        for (let index = 0; index < decompressedCellData.length; index++) {
            // @ts-ignore: TS2351: This expression is not constructable.
            polyData.cellData.arrays[index].data.values = new window[polyData.cellData.arrays[index].data.dataType](results[decompressedProps.length + decompressedPointData.length + index].outputs[0].data.buffer);
        }
        return polyData;
    });
}
// Custom View. Renders the widget model.
class ViewerView extends base_1.DOMWidgetView {
    constructor() {
        super(...arguments);
        this.itkVtkViewer = null;
        this.colorMapLoopBreak = false;
        this.skipOnCroppingPlanesChanged = false;
        this.use2D = false;
    }
    initialize_itkVtkViewer() {
        const rendered_image = this.model.get('rendered_image');
        const rendered_label_image = this.model.get('rendered_label_image');
        this.annotations_changed();
        this.axes_changed();
        const onBackgroundChanged = (background) => {
            this.model.set('background', background);
            this.model.save_changes();
        };
        this.itkVtkViewer.on('backgroundColorChanged', onBackgroundChanged);
        const background = this.model.get('background');
        if (background.length === 0) {
            this.model.set('background', this.itkVtkViewer.getBackgroundColor());
        }
        if (rendered_image) {
            this.interpolation_changed();
            this.cmap_changed();
            this.vmin_changed();
            this.vmax_changed();
        }
        if (rendered_image || rendered_label_image) {
            this.slicing_planes_changed();
            this.x_slice_changed();
            this.y_slice_changed();
            this.z_slice_changed();
        }
        if (rendered_image) {
            this.shadow_changed();
            this.gradient_opacity_changed();
            this.sample_distance_changed();
            this.channels_changed();
            this.blend_mode_changed();
        }
        this.ui_collapsed_changed();
        this.rotate_changed();
        if (rendered_image || rendered_label_image) {
            this.select_roi_changed();
            this.scale_factors_changed();
        }
        if (rendered_label_image) {
            this.label_image_names_changed();
            this.label_image_weights_changed();
            this.label_image_blend_changed();
            this.lut_changed();
        }
        const onUserInterfaceCollapsedToggle = (collapsed) => {
            if (collapsed !== this.model.get('ui_collapsed')) {
                this.model.set('ui_collapsed', collapsed);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('toggleUserInterfaceCollapsed', onUserInterfaceCollapsedToggle);
        const onRotateToggle = (rotate) => {
            if (rotate !== this.model.get('rotate')) {
                this.model.set('rotate', rotate);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('toggleRotate', onRotateToggle);
        const onAnnotationsToggle = (enabled) => {
            if (enabled !== this.model.get('annotations')) {
                this.model.set('annotations', enabled);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('toggleAnnotations', onAnnotationsToggle);
        const onAxesToggle = (enabled) => {
            if (enabled !== this.model.get('axes')) {
                this.model.set('axes', enabled);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('toggleAxes', onAxesToggle);
        const onInterpolationToggle = (enabled) => {
            if (enabled !== this.model.get('interpolation')) {
                this.model.set('interpolation', enabled);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('toggleInterpolation', onInterpolationToggle);
        const onSelectColorMap = (component, colorMap) => {
            let cmap = this.model.get('cmap');
            if (cmap !== null &&
                colorMap !== cmap[component] &&
                !this.colorMapLoopBreak) {
                cmap[component] = colorMap;
                this.model.set('cmap', cmap);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('selectColorMap', onSelectColorMap);
        const onSelectLookupTable = (lookupTable) => {
            let lut = this.model.get('lut');
            if (lut !== null && lookupTable !== lut) {
                this.model.set('lut', lookupTable);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('selectLookupTable', onSelectLookupTable);
        const onColorRangesChanged = (colorRanges) => {
            let vmin = this.model.get('vmin');
            if (vmin === null) {
                vmin = [];
            }
            let vmax = this.model.get('vmax');
            if (vmax === null) {
                vmax = [];
            }
            const rendered_image = this.model.get('rendered_image');
            const components = rendered_image.imageType.components;
            for (let component = 0; component < components; component++) {
                const colorRange = colorRanges[component];
                vmin[component] = colorRange[0];
                vmax[component] = colorRange[1];
            }
            this.model.set('vmax', vmax);
            this.model.set('vmin', vmin);
            this.model.save_changes();
        };
        this.itkVtkViewer.on('colorRangesChanged', onColorRangesChanged);
        const onCroppingPlanesChanged = (planes, bboxCorners) => {
            if (!this.model.get('_rendering_image') &&
                !this.skipOnCroppingPlanesChanged) {
                this.skipOnCroppingPlanesChanged = true;
                this.model.set('roi', new Float64Array([
                    bboxCorners[0][0],
                    bboxCorners[0][1],
                    bboxCorners[0][2],
                    bboxCorners[7][0],
                    bboxCorners[7][1],
                    bboxCorners[7][2]
                ]));
                this.model.save_changes();
            }
            else {
                this.skipOnCroppingPlanesChanged = false;
            }
        };
        this.itkVtkViewer.on('croppingPlanesChanged', onCroppingPlanesChanged);
        const onResetCrop = () => {
            this.model.set('_reset_crop_requested', true);
            this.model.save_changes();
        };
        this.itkVtkViewer.on('resetCrop', onResetCrop);
        const onToggleCroppingPlanes = (enabled) => {
            if (enabled !== this.model.get('select_roi')) {
                this.model.set('select_roi', enabled);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('toggleCroppingPlanes', onToggleCroppingPlanes);
        const onLabelMapWeightsChanged = ({ weights }) => {
            const typedWeights = new Float32Array(weights);
            this.model.set('label_image_weights', { shape: [weights.length],
                array: typedWeights
            });
            this.model.save_changes();
        };
        this.itkVtkViewer.on('labelMapWeightsChanged', onLabelMapWeightsChanged);
        const onLabelMapBlendChanged = (blend) => {
            this.model.set('label_image_blend', blend);
            this.model.save_changes();
        };
        this.itkVtkViewer.on('labelMapBlendChanged', onLabelMapBlendChanged);
        const onOpacityGaussiansChanged = macro_1.default.throttle((gaussians) => {
            this.model.set('opacity_gaussians', gaussians);
            this.model.save_changes();
        }, 100);
        this.itkVtkViewer.on('opacityGaussiansChanged', onOpacityGaussiansChanged);
        if (rendered_image) {
            const gaussians = this.model.get('opacity_gaussians');
            if (gaussians === null || gaussians.length === 0) {
                this.model.set('opacity_gaussians', this.itkVtkViewer.getOpacityGaussians());
            }
            this.opacity_gaussians_changed();
        }
        const onChannelsChanged = (channels) => {
            this.model.set('channels', channels);
            this.model.save_changes();
        };
        this.itkVtkViewer.on('componentVisibilitiesChanged', onChannelsChanged);
        const channels = this.model.get('channels');
        if (channels.length === 0) {
            this.model.set('channels', this.itkVtkViewer.getComponentVisibilities());
        }
        if (!this.use2D) {
            const onBlendModeChanged = (blend) => {
                let pythonMode = null;
                switch (blend) {
                    case 0:
                        pythonMode = 'composite';
                        break;
                    case 1:
                        pythonMode = 'max';
                        break;
                    case 2:
                        pythonMode = 'min';
                        break;
                    case 3:
                        pythonMode = 'average';
                        break;
                    default:
                        throw new Error('Unknown blend mode');
                }
                if (pythonMode !== this.model.get('blend')) {
                    this.model.set('blend', pythonMode);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('blendModeChanged', onBlendModeChanged);
            const onViewModeChanged = (mode) => {
                let pythonMode = null;
                switch (mode) {
                    case 'XPlane':
                        pythonMode = 'x';
                        break;
                    case 'YPlane':
                        pythonMode = 'y';
                        break;
                    case 'ZPlane':
                        pythonMode = 'z';
                        break;
                    case 'VolumeRendering':
                        pythonMode = 'v';
                        break;
                    default:
                        throw new Error('Unknown view mode');
                }
                if (pythonMode !== this.model.get('mode')) {
                    this.model.set('mode', pythonMode);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('viewModeChanged', onViewModeChanged);
            const onShadowToggle = (enabled) => {
                if (enabled !== this.model.get('shadow')) {
                    this.model.set('shadow', enabled);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('toggleShadow', onShadowToggle);
            const onSlicingPlanesToggle = (enabled) => {
                if (enabled !== this.model.get('slicing_planes')) {
                    this.model.set('slicing_planes', enabled);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('toggleSlicingPlanes', onSlicingPlanesToggle);
            const onXSliceChanged = (position) => {
                if (position !== this.model.get('x_slice')) {
                    this.model.set('x_slice', position);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('xSliceChanged', onXSliceChanged);
            if (this.model.get('x_slice') === null) {
                this.model.set('x_slice', this.itkVtkViewer.getXSlice());
                this.model.save_changes();
            }
            const onYSliceChanged = (position) => {
                if (position !== this.model.get('y_slice')) {
                    this.model.set('y_slice', position);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('ySliceChanged', onYSliceChanged);
            if (this.model.get('y_slice') === null) {
                this.model.set('y_slice', this.itkVtkViewer.getYSlice());
                this.model.save_changes();
            }
            const onZSliceChanged = (position) => {
                if (position !== this.model.get('z_slice')) {
                    this.model.set('z_slice', position);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('zSliceChanged', onZSliceChanged);
            if (this.model.get('z_slice') === null) {
                this.model.set('z_slice', this.itkVtkViewer.getZSlice());
                this.model.save_changes();
            }
            const onGradientOpacityChange = (opacity) => {
                if (opacity !== this.model.get('gradient_opacity')) {
                    this.model.set('gradient_opacity', opacity);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('gradientOpacityChanged', onGradientOpacityChange);
            const onVolumeSampleDistanceChange = (distance) => {
                if (distance !== this.model.get('sample_distance')) {
                    this.model.set('sample_distance', distance);
                    this.model.save_changes();
                }
            };
            this.itkVtkViewer.on('volumeSampleDistanceChanged', onVolumeSampleDistanceChange);
        } // end use2D
        const onCameraChanged = macro_1.default.throttle(() => {
            const camera = new Float32Array(9);
            const viewProxy = this.itkVtkViewer.getViewProxy();
            camera.set(viewProxy.getCameraPosition(), 0);
            camera.set(viewProxy.getCameraFocalPoint(), 3);
            camera.set(viewProxy.getCameraViewUp(), 6);
            this.model.set('camera', camera);
            this.model.save_changes();
        }, 50);
        // If view-up has not been set, set initial value to itk-vtk-viewer default
        const camera = this.model.get('camera');
        const cameraData = !!camera.slice ? camera : new Float32Array(camera.buffer);
        const viewUp = cameraData.slice(6, 9);
        if (!viewUp[0] && !viewUp[1] && !viewUp[2]) {
            onCameraChanged();
        }
        else {
            this.camera_changed();
        }
        const interactor = this.itkVtkViewer.getViewProxy().getInteractor();
        interactor.onEndMouseMove(onCameraChanged);
        interactor.onEndMouseWheel(onCameraChanged);
        interactor.onEndPan(onCameraChanged);
        interactor.onEndPinch(onCameraChanged);
        const vtkCamera = this.itkVtkViewer.getViewProxy().getCamera();
        vtkCamera.onModified(onCameraChanged);
        const onClickSlicePoint = (lastPickedValues) => {
            this.model.set('clicked_slice_point', lastPickedValues);
            this.model.save_changes();
        };
        this.itkVtkViewer
            .on('imagePicked', onClickSlicePoint);
        const point_sets = this.model.get('point_sets');
        if (point_sets) {
            this.point_set_colors_changed();
            this.point_set_opacities_changed();
            this.point_set_sizes_changed();
            this.point_set_representations_changed();
        }
        const onPointSetColorChanged = (index, color) => {
            const modelColors = this.model.get('point_set_colors');
            const modelColor = modelColors.array[index];
            if (color !== modelColor) {
                const newColors = modelColors.array.slice();
                newColors[index] = color;
                this.model.set('point_set_colors', { array: newColors, shape: modelColors.shape });
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('pointSetColorChanged', onPointSetColorChanged);
        const onPointSetOpacityChanged = (index, opacity) => {
            const modelOpacities = this.model.get('point_set_opacities');
            const modelOpacity = modelOpacities.array[index];
            if (opacity !== modelOpacity) {
                const newOpacities = modelOpacities.array.slice();
                newOpacities[index] = opacity;
                this.model.set('point_set_opacities', { array: newOpacities, shape: modelOpacities.shape });
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('pointSetOpacityChanged', onPointSetOpacityChanged);
        const onPointSetRepresentationChanged = (index, representation) => {
            const modelRepresentations = this.model.get('point_set_representations');
            const modelRepresentation = modelRepresentations[index];
            if (representation !== modelRepresentation) {
                modelRepresentations[index] = representation;
                this.model.set('point_set_representations', modelRepresentations);
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('pointSetRepresentationChanged', onPointSetRepresentationChanged);
        const onPointSetSizeChanged = (index, size) => {
            const modelSizes = this.model.get('point_set_sizes');
            const modelSize = modelSizes.array[index];
            if (size !== modelSize) {
                const newSize = modelSizes.array.slice();
                newSize[index] = size;
                this.model.set('point_set_sizes', { array: newSize, shape: modelSizes.shape });
                this.model.save_changes();
            }
        };
        this.itkVtkViewer.on('pointSetSizeChanged', onPointSetSizeChanged);
        const geometries = this.model.get('geometries');
        if (geometries) {
            this.geometry_colors_changed();
            this.geometry_opacities_changed();
        }
        this.mode_changed();
        this.units_changed();
    }
    render() {
        this.model.on('change:rendered_image', this.rendered_image_changed, this);
        this.model.on('change:rendered_label_image', this.rendered_label_image_changed, this);
        this.model.on('change:cmap', this.cmap_changed, this);
        this.model.on('change:lut', this.lut_changed, this);
        this.model.on('change:vmin', this.vmin_changed, this);
        this.model.on('change:vmax', this.vmax_changed, this);
        this.model.on('change:shadow', this.shadow_changed, this);
        this.model.on('change:slicing_planes', this.slicing_planes_changed, this);
        this.model.on('change:x_slice', this.x_slice_changed, this);
        this.model.on('change:y_slice', this.y_slice_changed, this);
        this.model.on('change:z_slice', this.z_slice_changed, this);
        this.model.on('change:gradient_opacity', this.gradient_opacity_changed, this);
        this.model.on('change:sample_distance', this.sample_distance_changed, this);
        this.model.on('change:blend_mode', this.blend_mode_changed, this);
        this.model.on('change:select_roi', this.select_roi_changed, this);
        this.model.on('change:_scale_factors', this.scale_factors_changed, this);
        this.model.on('change:point_sets', this.point_sets_changed, this);
        this.model.on('change:point_set_colors', this.point_set_colors_changed, this);
        this.model.on('change:point_set_opacities', this.point_set_opacities_changed, this);
        this.model.on('change:point_set_sizes', this.point_set_sizes_changed, this);
        this.model.on('change:point_set_representations', this.point_set_representations_changed, this);
        this.model.on('change:geometries', this.geometries_changed, this);
        this.model.on('change:geometry_colors', this.geometry_colors_changed, this);
        this.model.on('change:geometry_opacities', this.geometry_opacities_changed, this);
        this.model.on('change:interpolation', this.interpolation_changed, this);
        this.model.on('change:ui_collapsed', this.ui_collapsed_changed, this);
        this.model.on('change:rotate', this.rotate_changed, this);
        this.model.on('change:annotations', this.annotations_changed, this);
        this.model.on('change:axes', this.axes_changed, this);
        this.model.on('change:mode', this.mode_changed, this);
        this.model.on('change:units', this.units_changed, this);
        this.model.on('change:camera', this.camera_changed, this);
        this.model.on('change:background', this.background_changed, this);
        this.model.on('change:opacity_gaussians', this.opacity_gaussians_changed, this);
        this.model.on('change:channels', this.channels_changed, this);
        this.model.on('change:label_image_names', this.label_image_names_changed, this);
        this.model.on('change:label_image_blend', this.label_image_blend_changed, this);
        this.model.on('change:label_image_weights', this.label_image_weights_changed, this);
        let toDecompress = [];
        const rendered_image = this.model.get('rendered_image');
        if (rendered_image) {
            toDecompress.push(decompressImage(rendered_image));
        }
        const rendered_label_image = this.model.get('rendered_label_image');
        if (rendered_label_image) {
            toDecompress.push(decompressImage(rendered_label_image));
        }
        const point_sets = this.model.get('point_sets');
        if (point_sets && !!point_sets.length) {
            toDecompress = toDecompress.concat(point_sets.map(decompressPolyData));
        }
        const geometries = this.model.get('geometries');
        if (geometries && !!geometries.length) {
            toDecompress = toDecompress.concat(geometries.map(decompressPolyData));
        }
        const domWidgetView = this;
        Promise.all(toDecompress).then((decompressedData) => {
            let index = 0;
            let decompressedRenderedImage = null;
            let decompressedRenderedLabelMap = null;
            if (rendered_image) {
                decompressedRenderedImage = decompressedData[index];
                index++;
            }
            if (rendered_label_image) {
                decompressedRenderedLabelMap = decompressedData[index];
                index++;
            }
            let decompressedPointSets = null;
            if (point_sets && !!point_sets.length) {
                decompressedPointSets = decompressedData.slice(index, index + point_sets.length);
                index += point_sets.length;
            }
            let decompressedGeometries = null;
            if (geometries && !!geometries.length) {
                decompressedGeometries = decompressedData.slice(index, index + geometries.length);
                index += geometries.length;
            }
            return createRenderingPipeline(domWidgetView, {
                rendered_image: decompressedRenderedImage,
                rendered_label_image: decompressedRenderedLabelMap,
                point_sets: decompressedPointSets,
                geometries: decompressedGeometries
            });
        });
    }
    rendered_image_changed() {
        const rendered_image = this.model.get('rendered_image');
        if (rendered_image) {
            if (!rendered_image.data) {
                const domWidgetView = this;
                decompressImage(rendered_image).then((decompressed) => {
                    if (domWidgetView.itkVtkViewer) {
                        return Promise.resolve(replaceRenderedImage(domWidgetView, decompressed));
                    }
                    else {
                        const pipelineData = {
                            rendered_label_image: null,
                            rendered_image: decompressed,
                            point_sets: null,
                            geometries: null,
                        };
                        return createRenderingPipeline(domWidgetView, pipelineData);
                    }
                });
            }
            else {
                const domWidgetView = this;
                if (domWidgetView.itkVtkViewer) {
                    return Promise.resolve(replaceRenderedImage(this, rendered_image));
                }
                else {
                    const pipelineData = {
                        rendered_label_image: null,
                        rendered_image,
                        point_sets: null,
                        geometries: null,
                    };
                    return Promise.resolve(createRenderingPipeline(this, pipelineData));
                }
            }
        }
        return Promise.resolve(null);
    }
    rendered_label_image_changed() {
        const rendered_label_image = this.model.get('rendered_label_image');
        if (rendered_label_image) {
            if (!rendered_label_image.data) {
                const domWidgetView = this;
                decompressImage(rendered_label_image).then((decompressed) => {
                    if (domWidgetView.itkVtkViewer) {
                        return Promise.resolve(replaceRenderedLabelMap(domWidgetView, decompressed));
                    }
                    else {
                        const pipelineData = {
                            rendered_label_image: decompressed,
                            rendered_image: null,
                            point_sets: null,
                            geometries: null,
                        };
                        return createRenderingPipeline(domWidgetView, pipelineData);
                    }
                });
            }
            else {
                const domWidgetView = this;
                if (domWidgetView.itkVtkViewer) {
                    return Promise.resolve(replaceRenderedLabelMap(this, rendered_label_image));
                }
                else {
                    const pipelineData = {
                        rendered_label_image,
                        rendered_image: null,
                        point_sets: null,
                        geometries: null,
                    };
                    return Promise.resolve(createRenderingPipeline(this, pipelineData));
                }
            }
        }
        return Promise.resolve(null);
    }
    label_image_names_changed() {
        const label_image_names = this.model.get('label_image_names');
        if (label_image_names && this.itkVtkViewer) {
            const labelMapNames = new Map(label_image_names);
            this.itkVtkViewer.setLabelMapNames(labelMapNames);
        }
    }
    label_image_weights_changed() {
        const label_image_weights = this.model.get('label_image_weights');
        if (label_image_weights && this.itkVtkViewer) {
            const labelMapWeights = !!label_image_weights.array ? Array.from(label_image_weights.array) : Array.from(label_image_weights);
            this.itkVtkViewer.setLabelMapWeights(labelMapWeights);
        }
    }
    label_image_blend_changed() {
        const labelMapBlend = this.model.get('label_image_blend');
        if (this.itkVtkViewer) {
            this.itkVtkViewer.setLabelMapBlend(labelMapBlend);
        }
    }
    point_sets_changed() {
        const point_sets = this.model.get('point_sets');
        if (point_sets && !!point_sets.length) {
            if (!point_sets[0].points.values) {
                const domWidgetView = this;
                return Promise.all(point_sets.map(decompressPolyData)).then((decompressed) => {
                    if (domWidgetView.itkVtkViewer) {
                        return Promise.resolve(replacePointSets(domWidgetView, decompressed));
                    }
                    else {
                        const pipelineData = {
                            rendered_label_image: null,
                            rendered_image: null,
                            point_sets: decompressed,
                            geometries: null,
                        };
                        return createRenderingPipeline(domWidgetView, pipelineData);
                    }
                });
            }
            else {
                const domWidgetView = this;
                if (domWidgetView.itkVtkViewer) {
                    return Promise.resolve(replacePointSets(this, point_sets));
                }
                else {
                    const pipelineData = {
                        rendered_label_image: null,
                        rendered_image: null,
                        point_sets,
                        geometries: null,
                    };
                    return Promise.resolve(createRenderingPipeline(this, pipelineData));
                }
            }
        }
        return Promise.resolve(null);
    }
    point_set_colors_changed() {
        if (this.itkVtkViewer) {
            const point_set_colors = this.model.get('point_set_colors').array;
            const point_sets = this.model.get('point_sets');
            if (point_sets && !!point_sets.length) {
                point_sets.forEach((point_set, index) => {
                    const color = point_set_colors.slice(index * 3, (index + 1) * 3);
                    this.itkVtkViewer.setPointSetColor(index, color);
                });
            }
        }
    }
    point_set_opacities_changed() {
        if (this.itkVtkViewer) {
            const point_set_opacities = this.model.get('point_set_opacities').array;
            const point_sets = this.model.get('point_sets');
            if (point_sets && !!point_sets.length) {
                point_sets.forEach((point_set, index) => {
                    this.itkVtkViewer.setPointSetOpacity(index, point_set_opacities[index]);
                });
            }
        }
    }
    point_set_sizes_changed() {
        if (this.itkVtkViewer) {
            const point_set_sizes = this.model.get('point_set_sizes').array;
            const point_sets = this.model.get('point_sets');
            if (point_sets && !!point_sets.length) {
                point_sets.forEach((point_set, index) => {
                    this.itkVtkViewer.setPointSetSize(index, point_set_sizes[index]);
                });
            }
        }
    }
    point_set_representations_changed() {
        const point_set_representations = this.model.get('point_set_representations');
        if (this.itkVtkViewer) {
            const point_sets = this.model.get('point_sets');
            if (point_sets && !!point_sets.length) {
                point_set_representations.forEach((representation, index) => {
                    switch (representation.toLowerCase()) {
                        case 'hidden':
                            this.itkVtkViewer.setPointSetRepresentation(index, 'Hidden');
                            break;
                        case 'points':
                            this.itkVtkViewer.setPointSetRepresentation(index, 'Points');
                            break;
                        case 'spheres':
                            this.itkVtkViewer.setPointSetRepresentation(index, 'Spheres');
                            break;
                        default:
                            this.itkVtkViewer.setPointSetRepresentation(index, 'Points');
                    }
                });
            }
        }
    }
    geometries_changed() {
        const geometries = this.model.get('geometries');
        if (geometries && !!geometries.length) {
            if (!geometries[0].points.values) {
                const domWidgetView = this;
                return Promise.all(geometries.map(decompressPolyData)).then((decompressed) => {
                    if (domWidgetView.itkVtkViewer) {
                        return Promise.resolve(replaceGeometries(domWidgetView, decompressed));
                    }
                    else {
                        const pipelineData = {
                            rendered_label_image: null,
                            rendered_image: null,
                            point_sets: null,
                            geometries: decompressed,
                        };
                        return createRenderingPipeline(domWidgetView, pipelineData);
                    }
                });
            }
            else {
                const domWidgetView = this;
                if (domWidgetView.itkVtkViewer) {
                    return Promise.resolve(replaceGeometries(this, geometries));
                }
                else {
                    const pipelineData = {
                        rendered_label_image: null,
                        rendered_image: null,
                        point_sets: null,
                        geometries,
                    };
                    return Promise.resolve(createRenderingPipeline(this, pipelineData));
                }
            }
        }
        return Promise.resolve(null);
    }
    geometry_colors_changed() {
        const geometryColors = this.model.get('geometry_colors').array;
        if (this.itkVtkViewer) {
            const geometries = this.model.get('geometries');
            if (geometries && !!geometries.length) {
                geometries.forEach((geometry, index) => {
                    const color = geometryColors.slice(index * 3, (index + 1) * 3);
                    this.itkVtkViewer.setGeometryColor(index, color);
                });
            }
        }
    }
    geometry_opacities_changed() {
        const geometryOpacities = this.model.get('geometry_opacities').array;
        if (this.itkVtkViewer) {
            const geometries = this.model.get('geometries');
            if (geometries && !!geometries.length) {
                geometries.forEach((geometry, index) => {
                    this.itkVtkViewer.setGeometryOpacity(index, geometryOpacities[index]);
                });
            }
        }
    }
    ui_collapsed_changed() {
        const uiCollapsed = this.model.get('ui_collapsed');
        if (this.itkVtkViewer) {
            this.itkVtkViewer.setUserInterfaceCollapsed(uiCollapsed);
        }
    }
    rotate_changed() {
        var _a;
        const rotate = this.model.get('rotate');
        (_a = this.itkVtkViewer) === null || _a === void 0 ? void 0 : _a.setRotateEnabled(rotate);
    }
    annotations_changed() {
        var _a;
        const annotations = this.model.get('annotations');
        (_a = this.itkVtkViewer) === null || _a === void 0 ? void 0 : _a.setAnnotationsEnabled(annotations);
    }
    axes_changed() {
        var _a;
        const axes = this.model.get('axes');
        (_a = this.itkVtkViewer) === null || _a === void 0 ? void 0 : _a.setAxesEnabled(axes);
    }
    mode_changed() {
        const mode = this.model.get('mode');
        if (this.itkVtkViewer && !this.use2D) {
            switch (mode) {
                case 'x':
                    this.itkVtkViewer.setViewMode('XPlane');
                    break;
                case 'y':
                    this.itkVtkViewer.setViewMode('YPlane');
                    break;
                case 'z':
                    this.itkVtkViewer.setViewMode('ZPlane');
                    break;
                case 'v':
                    this.itkVtkViewer.setViewMode('VolumeRendering');
                    // Why is this necessary?
                    // Todo: fix in vtk.js
                    const viewProxy = this.itkVtkViewer.getViewProxy();
                    const representation = viewProxy.getRepresentations()[0];
                    const shadow = this.model.get('shadow');
                    !!representation && representation.setUseShadow(shadow);
                    break;
                default:
                    throw new Error('Unknown view mode');
            }
        }
    }
    units_changed() {
        const units = this.model.get('units');
        if (this.itkVtkViewer) {
            const viewProxy = this.itkVtkViewer.getViewProxy();
            viewProxy.setUnits(units);
        }
    }
    camera_changed() {
        const camera = this.model.get('camera');
        if (this.itkVtkViewer) {
            const cameraData = !!camera.slice ? camera : new Float32Array(camera.buffer);
            const viewProxy = this.itkVtkViewer.getViewProxy();
            viewProxy.setCameraPosition(...cameraData.subarray(0, 3));
            viewProxy.setCameraFocalPoint(...cameraData.subarray(3, 6));
            viewProxy.setCameraViewUp(...cameraData.subarray(6, 9));
            viewProxy.getCamera().computeDistance();
            viewProxy.renderLater();
        }
    }
    interpolation_changed() {
        const interpolation = this.model.get('interpolation');
        if (this.itkVtkViewer) {
            this.itkVtkViewer.setInterpolationEnabled(interpolation);
        }
    }
    cmap_changed() {
        const cmap = this.model.get('cmap');
        if (cmap !== null && this.itkVtkViewer) {
            for (let index = 0; index < cmap.length; index++) {
                if (cmap[index].startsWith('Custom')) {
                    const lutProxies = this.itkVtkViewer.getLookupTableProxies();
                    const lutProxy = lutProxies[index];
                    const customCmap = this.model.get('_custom_cmap');
                    const numPoints = customCmap.shape[0];
                    const rgbPoints = new Array(numPoints);
                    const cmapArray = customCmap.array;
                    const step = 1.0 / (numPoints - 1);
                    let xx = 0.0;
                    for (let pointIndex = 0; pointIndex < numPoints; pointIndex++) {
                        const rgb = cmapArray.slice(pointIndex * 3, (pointIndex + 1) * 3);
                        rgbPoints[pointIndex] = [xx, rgb[0], rgb[1], rgb[2]];
                        xx += step;
                    }
                    lutProxy.setRGBPoints(rgbPoints);
                }
                this.colorMapLoopBreak = true;
                this.itkVtkViewer.setColorMap(index, cmap[index]);
                this.colorMapLoopBreak = false;
            }
        }
    }
    lut_changed() {
        const lut = this.model.get('lut');
        if (lut !== null && this.itkVtkViewer) {
            //if (lut.startsWith('Custom')) {
            // -> from cmap, to be updated for lookup table
            //const lutProxies = this.itkVtkViewer.getLookupTableProxies()
            //const lutProxy = lutProxies[index]
            //const customCmap = this.model.get('_custom_cmap')
            //const numPoints = customCmap.shape[0]
            //const rgbPoints = new Array(numPoints)
            //const cmapArray = customCmap.array
            //const step = 1.0 / (numPoints - 1)
            //let xx = 0.0
            //for (let pointIndex = 0; pointIndex < numPoints; pointIndex++) {
            //const rgb = cmapArray.slice(pointIndex * 3, (pointIndex + 1) * 3)
            //rgbPoints[pointIndex] = [xx, rgb[0], rgb[1], rgb[2]]
            //xx += step
            //}
            //lutProxy.setRGBPoints(rgbPoints)
            //}
            this.itkVtkViewer.setLookupTable(lut);
        }
    }
    vmin_changed() {
        const vmin = this.model.get('vmin');
        if (vmin !== null && this.itkVtkViewer) {
            const rendered_image = this.model.get('rendered_image');
            for (let component = 0; component < rendered_image.imageType.components; component++) {
                let colorRange = this.itkVtkViewer.getColorRange(component);
                if (colorRange[0] && vmin.length > component) {
                    colorRange[0] = vmin[component];
                    this.itkVtkViewer.setColorRange(component, colorRange);
                }
            }
        }
    }
    vmax_changed() {
        const vmax = this.model.get('vmax');
        if (vmax !== null && this.itkVtkViewer) {
            const rendered_image = this.model.get('rendered_image');
            for (let component = 0; component < rendered_image.imageType.components; component++) {
                let colorRange = this.itkVtkViewer.getColorRange(component);
                if (colorRange[1] && vmax.length > component) {
                    colorRange[1] = vmax[component];
                    this.itkVtkViewer.setColorRange(component, colorRange);
                }
            }
        }
    }
    shadow_changed() {
        const shadow = this.model.get('shadow');
        if (this.itkVtkViewer && !this.use2D) {
            this.itkVtkViewer.setShadowEnabled(shadow);
        }
    }
    slicing_planes_changed() {
        const slicing_planes = this.model.get('slicing_planes');
        if (this.itkVtkViewer && !this.use2D) {
            this.itkVtkViewer.setSlicingPlanesEnabled(slicing_planes);
        }
    }
    x_slice_changed() {
        const position = this.model.get('x_slice');
        if (this.itkVtkViewer &&
            !this.use2D &&
            position !== null) {
            this.itkVtkViewer.setXSlice(position);
        }
    }
    y_slice_changed() {
        const position = this.model.get('y_slice');
        if (this.itkVtkViewer &&
            !this.use2D &&
            position !== null) {
            this.itkVtkViewer.setYSlice(position);
        }
    }
    z_slice_changed() {
        const position = this.model.get('z_slice');
        if (this.itkVtkViewer &&
            !this.use2D &&
            position !== null) {
            this.itkVtkViewer.setZSlice(position);
        }
    }
    gradient_opacity_changed() {
        const gradient_opacity = this.model.get('gradient_opacity');
        if (this.itkVtkViewer && !this.use2D) {
            this.itkVtkViewer.setGradientOpacity(gradient_opacity);
        }
    }
    sample_distance_changed() {
        const sample_distance = this.model.get('sample_distance');
        if (this.itkVtkViewer && !this.use2D) {
            this.itkVtkViewer.setVolumeSampleDistance(sample_distance);
        }
    }
    opacity_gaussians_changed() {
        const opacity_gaussians = this.model.get('opacity_gaussians');
        if (this.itkVtkViewer && !this.use2D) {
            this.itkVtkViewer.setOpacityGaussians(opacity_gaussians);
        }
    }
    channels_changed() {
        const channels = this.model.get('channels');
        if (this.itkVtkViewer) {
            this.itkVtkViewer.setComponentVisibilities(channels);
        }
    }
    blend_mode_changed() {
        const blend = this.model.get('blend_mode');
        if (this.itkVtkViewer && !this.use2D) {
            switch (blend) {
                case 'composite':
                    this.itkVtkViewer.setBlendMode(0);
                    break;
                case 'max':
                    this.itkVtkViewer.setBlendMode(1);
                    break;
                case 'min':
                    this.itkVtkViewer.setBlendMode(2);
                    break;
                case 'average':
                    this.itkVtkViewer.setBlendMode(3);
                    break;
                default:
                    throw new Error('Unexpected blend mode');
            }
        }
    }
    background_changed() {
        var _a;
        const background = this.model.get('background');
        (_a = this.itkVtkViewer) === null || _a === void 0 ? void 0 : _a.setBackgroundColor(background);
    }
    select_roi_changed() {
        var _a;
        const select_roi = this.model.get('select_roi');
        (_a = this.itkVtkViewer) === null || _a === void 0 ? void 0 : _a.setCroppingPlanesEnabled(select_roi);
    }
    scale_factors_changed() {
        let scaleFactors = this.model.get('_scale_factors');
        if (this.itkVtkViewer) {
            const viewProxy = this.itkVtkViewer.getViewProxy();
            if (typeof scaleFactors[0] === 'undefined') {
                scaleFactors = new Uint8Array(scaleFactors.buffer.buffer);
            }
            if (scaleFactors[0] === 1 &&
                scaleFactors[1] === 1 &&
                scaleFactors[2] === 1) {
                viewProxy.setSeCornerAnnotation(`${ANNOTATION_DEFAULT}`);
            }
            else {
                let scaleIndex = '';
                if (scaleFactors[0] === 1) {
                    scaleIndex = `${scaleIndex}<td>\${iIndex}</td>`;
                }
                else {
                    scaleIndex = `${scaleIndex}<td>${scaleFactors[0]}X</td>`;
                }
                if (scaleFactors[1] === 1) {
                    scaleIndex = `${scaleIndex}<td>\${jIndex}</td>`;
                }
                else {
                    scaleIndex = `${scaleIndex}<td>${scaleFactors[1]}X</td>`;
                }
                if (scaleFactors[2] === 1) {
                    scaleIndex = `${scaleIndex}<td>\${kIndex}</td>`;
                }
                else {
                    scaleIndex = `${scaleIndex}<td>${scaleFactors[2]}X</td>`;
                }
                viewProxy.setSeCornerAnnotation(`${ANNOTATION_CUSTOM_PREFIX}${scaleIndex}${ANNOTATION_CUSTOM_POSTFIX}`);
            }
        }
    }
    initialize_viewer() {
        this.initialize_itkVtkViewer();
        // possible to override in extensions
    }
}
exports.ViewerView = ViewerView;
//# sourceMappingURL=viewer.js.map