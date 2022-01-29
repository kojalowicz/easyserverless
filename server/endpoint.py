import base64

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def predict_image_object_detection_sample(
    project: str,
    endpoint_id: str,
    filename: str,
    location: str = "europe-west4",
    api_endpoint: str = "europe-west4-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    with open(filename, "rb") as f:
        file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageObjectDetectionPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    parameters = predict.params.ImageObjectDetectionPredictionParams(
        confidence_threshold=0.5, max_predictions=5,
    ).to_value()
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    return response.predictions


def print_bbox(image, predictions):
    im = Image.open(image)
    x = im.size[0]
    y = im.size[1]

    # Create figure and axes
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(im)

    for bbox in predictions[0].__dict__["_pb"]["bboxes"].list_value.values:
        x1 = bbox.list_value[0] * x
        x2 = bbox.list_value[1] * x
        y1 = bbox.list_value[2] * y
        y2 = bbox.list_value[3] * y
        dx = x2 - x1
        dy = y2 - y1
        # Create a Rectangle patch
        rect = patches.Rectangle((x1, y1), dx, dy, linewidth=1, edgecolor='r', facecolor='none')
        # Add the patch to the Axes
        ax.add_patch(rect)
    plt.show()


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/slupski/Desktop/ML-projects/salesrecon/easyserverless-337916-d2edcdf54171.json'

image = "/home/slupski/Downloads/test2.jpg"
predictions = predict_image_object_detection_sample(
    project="322035613717",
    endpoint_id="2200518591365775360",
    filename=image
)

print_bbox(image, predictions)