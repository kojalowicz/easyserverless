Files:  
- endpoint.py -script from the Internet that send request to VertexAI and get bbxoses from response
- server.py -like *endpoint.py* but code is reorganized a little and count statistics.
- mock_prediction.py -mock answer from VertexAI. For test purposes.
- send_image.py -sends request with image to Google Function for test purposes.
- image_recognition.py -code for Google Function to take image from the website, send it further to VertexAI, analyse response, and send it back to the caller.
