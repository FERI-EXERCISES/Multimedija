def prevzorci_sliko(slika: np.ndarray, nova_visina: int, nova_sirina: int) -> np.ndarray:
    # Preveri, ali je slika barvna ali sivinska
    if len(slika.shape) == 3:
        barvna = True
    elif len(slika.shape) == 2:
        barvna = False

    # Izračun razmerja med originalno in novo velikostjo slike
    razmerje_visina = nova_visina / slika.shape[0]
    razmerje_sirina = nova_sirina / slika.shape[1]

    # Filtriranje višjih frekvenc z uporabo Gaussovega filtra
    if barvna:
        slika = scipy.ndimage.gaussian_filter(slika, sigma=[razmerje_visina, razmerje_sirina, 0])
    else:
        slika = scipy.ndimage.gaussian_filter(slika, sigma=[razmerje_visina, razmerje_sirina])

    # Uporaba scipy.ndimage.zoom za prevzorčenje
    if barvna:
        prevzorcena_slika = scipy.ndimage.zoom(slika, (razmerje_visina, razmerje_sirina, 1))
    else:
        prevzorcena_slika = scipy.ndimage.zoom(slika, (razmerje_visina, razmerje_sirina))

    # Pretvarjanje podatkovnega tipa na isti tip kot vhodna slika
    prevzorcena_slika = prevzorcena_slika.astype(slika.dtype)

    return prevzorcena_slika


def RGB_v_YCbCr(slika: np.ndarray) -> np.ndarray:
    # Definiraj koeficiente za pretvorbo v YCbCr
    YCbCr_from_RGB = np.array([[0.299, 0.587, 0.114],
                               [-0.168736, -0.331264, 0.5],
                               [0.5, -0.418688, -0.081312]])

    YCbCr = np.dot(slika, YCbCr_from_RGB.T)
    YCbCr[:, :, [1, 2]] += 128
    return np.uint8(YCbCr)

def YCbCr_v_RGB(slika: np.ndarray) -> np.ndarray:
    # Definiraj koeficiente za pretvorbo v RGB
    RGB_from_YCbCr = np.array([[1., 0., 1.402],
                               [1., -0.344136, -0.714136],
                               [1., 1.772, 0.]])

    RGB = slika.astype(np.float64)
    RGB[:, :, [1, 2]] -= 128
    RGB = np.dot(RGB, RGB_from_YCbCr.T)
    np.putmask(RGB, RGB > 255, 255)
    np.putmask(RGB, RGB < 0, 0)
    return np.uint8(RGB)

def Compression(video_frame, print_bits=False):
    video_frame = cv2.resize(video_frame, (640, 360), interpolation=cv2.INTER_AREA)

    # convert frame to YCbCr
    frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2YCrCb)

    # split frame into Y, Cb, Cr
    Y, Cb, Cr = cv2.split(frame)

    if print_bits:
        # print bits
        print("Cb: ", bin(Cb[0][0]))
        print("Cr: ", bin(Cr[0][0]))

    # get 4 MSB bits from Cb and Cr
    Cb = (Cb >> 4) << 4 # shift bits to MSB
    Cr = Cr >> 4

    if print_bits:
        # print bits
        print("Cb: ", bin(Cb[0][0]))
        print("Cr: ", bin(Cr[0][0]))

    # merge Cb and Cr value into one byte
    CbCr = Cb | Cr

    if print_bits:
        print("Y: ", bin(Y[0][0]))
        print("CbCr: ", bin(CbCr[0][0]))

    # merge Y and CbCr into one matrix
    frame = cv2.merge([Y, CbCr])

    if print_bits:
        print("YCbCr: ", bin(frame[0][0][0]), bin(frame[0][0][1]))

    return frame

def Decompression(frame, print_bits=False):
    # split frame into Y, CbCr
    Y, CbCr = cv2.split(frame)

    if print_bits:
        print("Y: ", bin(Y[0][0]))
        print("CbCr: ", bin(CbCr[0][0]))

    # get first 4 bits from CbCr
    Cb = (CbCr >> 4) << 4

    # get last 4 bits from CbCr
    Cr = CbCr << 4

    if print_bits:
        print("Cb: ", bin(Cb[0][0]))
        print("Cr: ", bin(Cr[0][0]))

    # merge Y, Cb, Cr into one matrix
    video_frame = cv2.merge([Y, Cb, Cr])

    if print_bits:
        print("Y: ", bin(video_frame[0][0][0]))
        print("Cb: ", bin(video_frame[0][0][1]))
        print("Cr: ", bin(video_frame[0][0][2]))

    video_frame = cv2.resize(video_frame, (1920, 1080), interpolation=cv2.INTER_LINEAR)

    return cv2.cvtColor(video_frame, cv2.COLOR_YCrCb2BGR)