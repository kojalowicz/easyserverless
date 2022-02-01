import base64
from collections import Counter

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

from mock_prediction import mock_prediction

CONFIDENCE_THRESHOLD: float = 0.5
MAX_PREDICTIONS: int = 5


def predict_image_object_detection_sample(
        project: str,
        endpoint_id: str,
        encoded_image: str,
        api_endpoint: str = "europe-west4-aiplatform.googleapis.com",
        location: str = "europe-west4"
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # The format of each instance should conform to the deployed model's prediction input schema.
    instance = predict.instance.ImageObjectDetectionPredictionInstance(content=encoded_image, ).to_value()
    parameters = predict.params.ImageObjectDetectionPredictionParams(confidence_threshold=CONFIDENCE_THRESHOLD, max_predictions=MAX_PREDICTIONS,).to_value()
    endpoint = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)

    response = client.predict(endpoint=endpoint, instances=[instance], parameters=parameters)
    return response.predictions


def print_bbox(image, predictions) -> None:
    im = Image.open(image)
    x = im.size[0]
    y = im.size[1]

    # Create figure and axes
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(im)

    for bbox in predictions[0].get("bboxes"):
        x1 = bbox[0] * x
        x2 = bbox[1] * x
        y1 = bbox[2] * y
        y2 = bbox[3] * y
        dx = x2 - x1
        dy = y2 - y1
        # Create a Rectangle patch
        rect = patches.Rectangle((x1, y1), dx, dy, linewidth=1, edgecolor='r', facecolor='none')
        # Add the patch to the Axes
        ax.add_patch(rect)
    plt.show()


def take_input(filename):
    with open(filename, "rb") as f:
        file_content = f.read()

    encoded_content = base64.b64encode(file_content).decode("utf-8")
    return encoded_content


def count_stats(predictions):
    counter = Counter(predictions[0].get("displayNames"))
    print(f"all: {len(list(counter.elements()))}")
    for label in counter.keys():
        print(f"{label}: {counter[label]}")
    return counter


if __name__ == '__main__':
    mock = True
    filename = "D:\\projects\\GoogleHackaton\\testAI\\20220122_170004_2.jpg"
    image = take_input(filename)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:\\projects\\GoogleHackaton\\salesrecon-05089e0947a7.json'

    if mock:
        predictions = mock_prediction()
    else:
        predictions = predict_image_object_detection_sample(
            project="728620304704",
            endpoint_id="2872117885797400576",
            encoded_image=image
        )

    count_stats(predictions)
    # print_bbox(filename, predictions)

