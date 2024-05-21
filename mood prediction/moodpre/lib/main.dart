import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:image/image.dart' as img;

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Mood Prediction')),
        body: MoodPrediction(),
      ),
    );
  }
}

class MoodPrediction extends StatefulWidget {
  @override
  _MoodPredictionState createState() => _MoodPredictionState();
}

class _MoodPredictionState extends State<MoodPrediction> {
  CameraController? _controller;
  String _result = '';
  bool _isDetecting = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    final camera = cameras.first;

    _controller = CameraController(camera, ResolutionPreset.medium);
    await _controller?.initialize();

    _controller?.startImageStream((CameraImage image) {
      if (!_isDetecting) {
        _isDetecting = true;
        _predictMood(image);
      }
    });

    setState(() {});
  }

  Future<void> _predictMood(CameraImage image) async {
    final bytes = _convertYUV420ToImage(image);
    final request = http.MultipartRequest('POST', Uri.parse('http://192.168.0.104:5000/predict'));
    request.files.add(http.MultipartFile.fromBytes('image', bytes, filename: 'image.jpg'));

    final response = await request.send();

    if (response.statusCode == 200) {
      final responseData = await response.stream.bytesToString();
      final data = json.decode(responseData);
      setState(() {
        _result = 'Mood: ${data['mood']}, Confidence: ${data['confidence']}';
      });
    } else {
      setState(() {
        _result = 'Failed to predict mood';
      });
    }

    await Future.delayed(Duration(seconds: 7));
    _isDetecting = false;
  }

  Uint8List _convertYUV420ToImage(CameraImage image) {
    final int width = image.planes.first.width ?? 0;
    final int height = image.planes.first.height ?? 0;
    final int uvRowStride = image.planes[1].bytesPerRow ?? 0;
    final int uvPixelStride = image.planes[1].bytesPerPixel ?? 1;

    final img.Image imgBuffer = img.Image(width, height);
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final int uvIndex = uvPixelStride * (x ~/ 2) + uvRowStride * (y ~/ 2);
        final int index = y * width + x;

        final int yp = image.planes.first.bytes[index];
        final int up = image.planes[1].bytes[uvIndex];
        final int vp = image.planes[2].bytes[uvIndex];

        int r = (yp + vp * 1436 / 1024 - 179).toInt();
        int g = (yp - up * 46549 / 131072 + 44 - vp * 93604 / 131072 + 91).toInt();
        int b = (yp + up * 1814 / 1024 - 227).toInt();

        r = r.clamp(0, 255);
        g = g.clamp(0, 255);
        b = b.clamp(0, 255);

        imgBuffer.setPixel(x, y, Color.fromARGB(255, r, g, b).value);
      }
    }

    return Uint8List.fromList(img.encodeJpg(imgBuffer));
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        if (_controller != null && _controller!.value.isInitialized)
          Container(
            height: 400,
            child: CameraPreview(_controller!),
          ),
        SizedBox(height: 20),
        Text(_result),
      ],
    );
  }
}
