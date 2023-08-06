import cv2 


def __variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def is_blur(image_path:str):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = __variance_of_laplacian(gray)
    return True if fm < 100 else False

def chunk_list(datas, chunksize=100):
    """Split list into the chucks

    Params:
        datas     (list): data that want to split into the chunk
        chunksize (int) : how much maximum data in each chunks

    Returns:
        chunks (obj): the chunk of list
    """
    for i in range(0, len(datas), chunksize):
        yield datas[i:i + chunksize]