import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'authentication.dart';
import 'dart:async';
void main() {
  runApp(MyApp());
  // Hide the status and navigation bars
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Accessible Lock App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: FrontPage(),
    );
  }
}

class FrontPage extends StatefulWidget {
  @override
  _FrontPageState createState() => _FrontPageState();
}

class _FrontPageState extends State<FrontPage> {
  final FlutterTts flutterTts = FlutterTts();
  final stt.SpeechToText speech = stt.SpeechToText();
  String _amount = "";
  bool _awaitingConfirmation = false;
  bool _isListening = false;
  int _tapCounter = 0;
  DateTime _lastTapTime = DateTime.now();
  Timer? _tapTimer;

  @override
  void initState() {
    super.initState();
    _initializeTts();
    _initializeSpeech();
  }

  Future<void> _initializeTts() async {
    await flutterTts.setLanguage('en-US');
    await flutterTts.setSpeechRate(0.5);
  }

  Future<void> _initializeSpeech() async {
    bool available = await speech.initialize(
      onStatus: (status) {
        print('onStatus: $status');
        if (status == 'done' && !_awaitingConfirmation) {
          _startListening();
        }
      },
      onError: (error) => print('onError: $error'),
    );
    if (available) {
      _startListening();
    } else {
      print("The user has denied the use of speech recognition.");
    }
  }

  Future<void> _startListening() async {
    if (!_isListening) {
      setState(() {
        _isListening = true;
      });
      await flutterTts.speak("tell me the amount you want to transfer: ");
      speech.listen(
        onResult: (val) {
          if (val.finalResult) {
            if (_awaitingConfirmation) {
              _handleConfirmation(val.recognizedWords);
            } else {
              _processCommand(val.recognizedWords);
            }
          }
        },
      ).then((_) {
        setState(() {
          _isListening = false;
        });
      });
    }
  }

  void _processCommand(String command) {
    final paymentIntent = _extractPaymentIntent(command);
    if (paymentIntent != null) {
      setState(() => _amount = paymentIntent['amount']!);
      _awaitConfirmation();
    } else {
      flutterTts.speak("I didn't understand your request. Please try again.");
      _startListening();
    }
  }

  Map<String, String>? _extractPaymentIntent(String command) {
    final words = command.split(' ');
    for (final word in words) {
      if (double.tryParse(word) != null) {
        return {
          'intent': 'payment',
          'amount': word,
        };
      }
    }
    return null;
  }

  Future<void> _awaitConfirmation() async {
    setState(() => _awaitingConfirmation = true);
    await flutterTts.speak("Proceed with $_amount? Double-tap for yes, triple-tap for no.");
  }

  void _handleTap() {
    DateTime now = DateTime.now();
    if (now.difference(_lastTapTime) < Duration(seconds: 1)) {
      _tapCounter++;
    } else {
      _tapCounter = 1;
    }
    _lastTapTime = now;

    if (_tapCounter == 2) {
      // Start a timer to handle triple tap
      _tapTimer = Timer(Duration(seconds: 1), () {
        // If the timer completes without another tap, treat it as a double-tap
        _handleConfirmation("yes");
      });
    } else if (_tapCounter == 3) {
      // If the third tap happens within the delay, treat it as a triple-tap
      _tapTimer?.cancel(); // Cancel the previous timer
      _handleConfirmation("no");
    }
  }

  void _handleConfirmation(String confirmation) async {
    if (confirmation.toLowerCase() == "yes") {
      speech.stop();
      await flutterTts.speak("Proceeding with SSFD authentication.");
      await Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => AuthenticationPage()),
      );
      setState(() => _awaitingConfirmation = false);
      _startListening();
    } else if (confirmation.toLowerCase() == "no") {
      speech.stop();
      setState(() => _awaitingConfirmation = false);
      await flutterTts.speak("Operation cancelled. How can I assist you?");
      _startListening();
    } else {
      await flutterTts.speak("Please say yes or no.");
      _startListening();
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _handleTap,
      child: Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                "Amount:",
                style: TextStyle(color: Colors.white, fontSize: 24),
              ),
              Text(
                _amount,
                style: TextStyle(color: Colors.white, fontSize: 48),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
