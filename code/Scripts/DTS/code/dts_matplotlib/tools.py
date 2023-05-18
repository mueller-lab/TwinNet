from PIL import Image

class NumpyArray:

    cdict = {

        'red'  :  ( (0.0, 0.25, .25), (0.02, .59, .59), (1., 1., 1.)),
        
        'green'  :  ( (0.0, 0.25, .25), (0.02, .59, .59), (1., 1., 1.)),
        
        'blue'  :  ( (0.0, 0.25, .25), (0.02, .59, .59), (1., 1., 1.)),
    }

    cdict2 = {

        'red':   [(0.0,  0.0, 0.0),
                  (0.5,  1.0, 1.0),
                  (1.0,  1.0, 1.0)],
        
        'green': [(0.0,  0.0, 0.0),
                  (0.25, 0.0, 0.0),
                  (0.75, 1.0, 1.0),
                  (1.0,  1.0, 1.0)],
        
        'blue':  [(0.0,  0.0, 0.0),
                  (0.5,  0.0, 0.0),
                  (1.0,  1.0, 1.0)]
    }

    def normalize(v):
        return v/np.linalg.norm(v)

    def image_from_matrix(arr_):
        # See: https://stackoverflow.com/questions/7694772/turning-a-large-matrix-into-a-grayscale-image
        return Image.fromarray(arr_)
