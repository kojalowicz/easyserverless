import logging
from collections import Counter

from flask import abort, Request, make_response, jsonify
from google.cloud import aiplatform
from google.cloud.aiplatform.v1.schema import predict


CONFIDENCE_THRESHOLD: float = 0.5
MAX_PREDICTIONS: int = 5
ENDPOINT_ID: str = "2872117885797400576"


def load_argument(request: Request, argument: str):
    value = None
    request_json = request.get_json()

    if request.args and argument in request.args:
        value = request.args.get(argument)
    elif request_json and argument in request_json:
        value = request_json[argument]
    else:
        logging.error(f"{argument} not provided.")
        abort(400)

    return value


def mock_prediction():
    return [{'confidences': [0.997850418, 0.99748683, 0.989509, 0.934005201, 0.913826168],
            'bboxes': [[0.400397032, 0.472672701, 0.64531219, 0.820441425],
                       [0.471109, 0.548620641, 0.643198967, 0.828915119],
                       [0.323561281, 0.393450409, 0.0354692228, 0.205512658],
                       [0.337716, 0.39868772, 0.649659514, 0.780516326],
                       [0.544878304, 0.61407119, 0.639214694, 0.826832771]],
            'displayNames': ['cola_front', 'cola_front', 'cola_front', 'cola_front', 'cola_back'],
            'ids': ['2198308572993945600', '2198308572993945600', '2198308572993945600', '2198308572993945600',
                    '6809994591421333504']}]


def predict_image_object_detection_sample(
        encoded_image: str,
        endpoint_id: str,
        project: str = "728620304704",
        api_endpoint: str = "europe-west4-aiplatform.googleapis.com",
        location: str = "europe-west4"
):
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # The format of each instance should conform to the deployed model's prediction input schema.
    instance = predict.instance.ImageObjectDetectionPredictionInstance(content=encoded_image, ).to_value()
    parameters = predict.params.ImageObjectDetectionPredictionParams(confidence_threshold=CONFIDENCE_THRESHOLD,
                                                                     max_predictions=MAX_PREDICTIONS,).to_value()
    endpoint = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)

    response = client.predict(endpoint=endpoint, instances=[instance], parameters=parameters)
    return response.predictions


def call_vertex(image: str):
    logging.info("Start prediction.")
    return predict_image_object_detection_sample(encoded_image=image, endpoint_id=ENDPOINT_ID)


def get_labels(predictions) -> dict[str: list]:
    labels2 = list(predictions[0].get("displayNames"))
    bboxes = [list(b) for b in predictions[0].get("bboxes")]
    return {
        'labels': labels2,
        'bboxes': bboxes
    }


def count_statistics(labels: list[str]) -> dict[str: int]:
    separator: str = '_'
    counter = Counter(labels)
    prefix = next(iter(counter.keys())).split(separator)[0]
    front: int = counter[prefix+separator+"front"]
    back: int = counter[prefix+separator+"back"]
    all_products: int = front + back
    return {
        'all': all_products,
        'front': front,
        'back': back
    }


def check_rules(stats: dict[str: bool]):
    count_rule = stats['all'] >= 5
    face_rule = stats['front'] >= 3

    return {
        'count_rule': count_rule,
        'face_rule': face_rule
    }


def join_outputs(labels, stats, rules) -> dict:
    return {
        'stats': stats,
        'rules': rules,
        'labels': labels
    }


def prepare_response(output):
    json = jsonify(output)
    response = make_response(json, 200)
    response.headers['Content-Type'] = 'application/json'
    return response


def recognize_product(request: Request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    product: str = load_argument(request, 'product')
    logging.info(f"Product={product}")
    image = load_argument(request, 'image')
    logging.info(f"Image provided: {image is not None}")
    image_decoded: str = image

    predictions = call_vertex(image_decoded)
    labels = get_labels(predictions)
    logging.info(f"Labels={str(labels)}")
    stats: dict[str: int] = count_statistics(labels.get("labels"))
    logging.info(f"Stats={str(stats)}")
    rules: dict[str: bool] = check_rules(stats)
    logging.info(f"Rules={str(rules)}")

    output = join_outputs(labels, stats, rules)
    logging.info(f"Output={str(output)}")
    return prepare_response(output)
