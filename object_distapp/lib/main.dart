import 'dart:async'; // Import the async library for Timer
import 'dart:convert';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'package:flutter_tts/flutter_tts.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: CameraScreen(),
    );
  }
}

class CameraScreen extends StatefulWidget {
  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? controller;
  List<CameraDescription>? cameras;
  bool isCameraInitialized = false;
  String detectedClass = '';
  double distance = 0;
  FlutterTts flutterTts = FlutterTts();
  late Timer timer; // Timer for periodic object detection

  @override
  void initState() {
    super.initState();
    initCamera();
    startTimer(); // Start the timer when the screen initializes
  }

  Future<void> initCamera() async {
    cameras = await availableCameras();
    controller = CameraController(cameras![0], ResolutionPreset.medium);
    await controller!.initialize();
    setState(() {
      isCameraInitialized = true;
    });
  }

  void startTimer() {
    timer = Timer.periodic(Duration(seconds: 7), (Timer t) {
      // Call captureAndDetect every 7 seconds
      captureAndDetect();
    });
  }

  Future<void> captureAndDetect() async {
    final image = await controller!.takePicture();
    final imageFile = File(image.path);

    // Send the image to the Flask backend for object detection
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('http://192.168.130.6:5000/detect'),
    );
    request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));

    final response = await request.send();
    final responseData = await http.Response.fromStream(response);

    if (response.statusCode == 200) {
      final List<dynamic> objects = jsonDecode(responseData.body);
      if (objects.isNotEmpty) {
        setState(() {
          detectedClass = objects[0]['class_name'];
          distance = objects[0]['distance'];
        });
        await flutterTts.speak('Detected $detectedClass at a distance of ${distance.toStringAsFixed(2)} meters.');
      }
    } else {
      setState(() {
        detectedClass = 'Error';
        distance = 0;
      });
      await flutterTts.speak('Error in object detection.');
    }
  }

  @override
  void dispose() {
    controller?.dispose();
    timer.cancel(); // Cancel the timer when the screen is disposed
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Object Detection')),
      body: Column(
        children: [
          if (isCameraInitialized)
            AspectRatio(
              aspectRatio: controller!.value.aspectRatio,
              child: CameraPreview(controller!),
            ),
          SizedBox(height: 20),
          Text('Detected Class: $detectedClass'),
          Text('Distance: ${distance.toStringAsFixed(2)} meters'),
        ],
      ),
    );
  }
}
