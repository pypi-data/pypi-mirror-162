from requests import get

def return_cifar10():

        url = "https://github.com/nobug-code/test_nk_2/raw/main/airplane.zip"

        file_name = './down.zip'
        with open(file_name, "wb") as file:  # open in binary mode
                response = get(url)  # get request
                file.write(response.content)  # write to file
