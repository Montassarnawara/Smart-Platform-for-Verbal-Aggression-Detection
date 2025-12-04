# 🎙️ Smart Platform for Verbal Aggression Detection

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-green)](https://www.mongodb.com/)

## 📋 Overview

A comprehensive AI-powered platform for detecting verbal aggression in real-time audio streams. This project combines machine learning, audio processing, and IoT technologies to create an intelligent system capable of identifying aggressive vocal patterns and alerting in dangerous situations.

## 👨‍💻 Author

**Montassar Nawara**

- GitHub: [@Montassarnawara](https://github.com/Montassarnawara)
- Project: Research Internship - AI & Automation

## 🚀 Features

- **Real-time Audio Analysis**: Continuous monitoring and processing of audio streams
- **Machine Learning Models**: Advanced classification using trained models for aggression detection
- **ESP32 Integration**: IoT hardware integration for audio capture and alerts
- **MongoDB Database**: Efficient storage and retrieval of audio analysis results
- **REST API**: Complete API system for audio processing and predictions
- **Automated Pipeline**: End-to-end automation from audio capture to alert generation

## 📁 Project Structure

```
├── 1-objectif&test_APIs_with_py/     # Initial API development and testing
├── 2-test_ConnMongodb/                # MongoDB connection and integration tests
├── 3-first_project_automatise/        # First automated system with ESP32
├── 4-avencement&train_model/          # Model training and advancement
├── 5-rapports/                        # Project reports and documentation
├── 6-papier/                          # Research papers and datasheets
└── 7-project_final_apis/              # Final production-ready API system
```

## 🛠️ Technologies Used

- **Programming Languages**: Python, C++ (Arduino/ESP32)
- **Machine Learning**: scikit-learn, librosa, audio processing
- **Databases**: MongoDB
- **Hardware**: ESP32 microcontroller
- **APIs**: FastAPI/Flask
- **Audio Processing**: Wave analysis, feature extraction, noise reduction

## 📊 Key Components

### 1. Audio Analysis Engine
- Feature extraction (MFCC, ZCR, spectral features)
- Real-time audio segmentation
- Noise filtering and preprocessing

### 2. Machine Learning Models
- Trained classifiers for aggression detection
- Model evaluation and validation
- Continuous improvement pipeline

### 3. IoT Integration
- ESP32-based audio capture
- WiFi connectivity
- Alert system activation

### 4. API System
- RESTful endpoints for audio analysis
- Real-time prediction services
- Database integration

## 🔧 Installation

### Prerequisites
```bash
Python 3.8+
MongoDB
ESP32 development environment
```

### Setup
```bash
# Clone the repository
git clone https://github.com/Montassarnawara/Smart-Platform-for-Verbal-Aggression-Detection.git

# Navigate to project directory
cd Smart-Platform-for-Verbal-Aggression-Detection

# Install dependencies (example for final system)
cd 7-project_final_apis/sys_automa_final
pip install -r requirements.txt
```

## 🎯 Usage

### Running the API System
```bash
cd 7-project_final_apis/sys_automa_final
python audio_api_system.py
```

### Testing the Model
```bash
python quick_test.py
```

## 📈 Model Performance

The system includes multiple trained models with various configurations:
- **Zeta Level Max Model**: Advanced feature extraction with high accuracy
- **Best Audio Model**: Optimized for real-time processing
- **Environment-aware Model**: Noise-robust classification

## 🔬 Research & Development

This project was developed as part of a research internship focusing on:
- Automatic verbal aggression detection
- Real-time audio classification
- IoT integration for smart monitoring systems
- Machine learning model optimization

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Montassar Nawara

## 🙏 Acknowledgments

- Research institution: ENSI-UMA
- Internship supervisor and research team
- Open-source community for libraries and tools

## 📧 Contact

For questions or collaboration opportunities, please open an issue or contact through GitHub.

---

**Note**: This is a research project. Please ensure compliance with privacy laws and ethical guidelines when deploying audio monitoring systems.
