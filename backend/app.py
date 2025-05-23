from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import io

app = Flask(__name__)

# In-memory storage (replace with a more robust solution for a real app)
knn_classifier = None
training_features_list = [] # Use a list to append, then convert to numpy array
training_labels_list = []
model_trained = False
IMAGE_SIZE = (32, 32)

def preprocess_image(image_file_storage):
    try:
        # For FileStorage object, image_file_storage.stream contains the file-like object
        image = Image.open(image_file_storage.stream)
        image = image.convert('L') # Grayscale
        image = image.resize(IMAGE_SIZE)
        feature_vector = np.array(image).flatten()
        return feature_vector
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

@app.route('/train_model', methods=['POST'])
def train_model_route():
    global knn_classifier, training_features_list, training_labels_list, model_trained
    
    # Reset model and data
    knn_classifier = None
    training_features_list = []
    training_labels_list = []
    model_trained = False

    category1_label = request.form.get('category1_label', 'Category1')
    category2_label = request.form.get('category2_label', 'Category2')
    
    cat1_images = request.files.getlist('category1_images')
    cat2_images = request.files.getlist('category2_images')

    if not cat1_images and not cat2_images:
        return jsonify({"message": "No image files provided for training."}), 400

    for img_fs in cat1_images:
        if img_fs and img_fs.filename != '': # Check if file exists and has a name
            features = preprocess_image(img_fs)
            if features is not None:
                training_features_list.append(features)
                training_labels_list.append(category1_label)
            
    for img_fs in cat2_images:
        if img_fs and img_fs.filename != '': # Check if file exists and has a name
            features = preprocess_image(img_fs)
            if features is not None:
                training_features_list.append(features)
                training_labels_list.append(category2_label)

    if not training_features_list:
        return jsonify({"message": "No valid training images processed successfully."}), 400

    # Convert lists to numpy arrays for scikit-learn
    X_train = np.array(training_features_list)
    y_train = np.array(training_labels_list)

    if X_train.size == 0: # Should be caught by the previous check, but good to have
        return jsonify({"message": "Training features are empty after processing."}), 400
        
    # Ensure n_neighbors is not greater than the number of samples
    n_samples = len(X_train)
    knn_classifier = KNeighborsClassifier(n_neighbors=min(3, n_samples)) 
    
    try:
        knn_classifier.fit(X_train, y_train)
        model_trained = True
    except Exception as e:
        print(f"Error training model: {e}")
        return jsonify({"message": f"Error during model training: {e}"}), 500
    
    return jsonify({"message": f"Model trained successfully with {len(X_train)} samples."})

@app.route('/classify_image', methods=['POST'])
def classify_image_route():
    global knn_classifier, model_trained
    
    if not model_trained or knn_classifier is None:
        return jsonify({"error": "Model not trained yet. Please train first."}), 400
        
    if 'image' not in request.files or request.files['image'].filename == '':
        return jsonify({"error": "No image provided for classification."}), 400
        
    image_fs = request.files['image']
    features = preprocess_image(image_fs)
    
    if features is None:
        return jsonify({"error": "Could not process image for classification."}), 400
        
    try:
        prediction = knn_classifier.predict(features.reshape(1, -1))
        return jsonify({"result": prediction[0]})
    except Exception as e:
        print(f"Error during classification: {e}")
        return jsonify({"error": f"Error during classification: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
