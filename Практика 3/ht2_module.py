def convolve2d(image, kernel):
    img_h = len(image)
    img_w = len(image[0])
    ker_h = len(kernel)
    ker_w = len(kernel[0])

    out_h = img_h - ker_h + 1
    out_w = img_w - ker_w + 1

    result = [[0.0 for _ in range(out_w)] for _ in range(out_h)]

    for i in range(out_h):
        for j in range(out_w):
            conv_sum = 0.0
            for ki in range(ker_h):
                for kj in range(ker_w):
                    conv_sum += image[i + ki][j + kj] * kernel[ki][kj]
            result[i][j] = conv_sum

    return result


def multichannel_filter_decorator(func):
    def wrapper(image, kernel):

        is_multichannel = isinstance(image[0][0], (list, tuple))

        if not is_multichannel:
            return func(image, kernel)

        M = len(image)
        N = len(image[0])
        C = len(image[0][0])

        filtered_channels = []
        for c in range(C):
            channel_2d = [[image[i][j][c] for j in range(N)] for i in range(M)]

            filtered_channel = func(channel_2d, kernel)
            filtered_channels.append(filtered_channel)

        out_M = len(filtered_channels[0])
        out_N = len(filtered_channels[0][0])

        result = []
        for i in range(out_M):
            row = []
            for j in range(out_N):
                pixel = [filtered_channels[c][i][j] for c in range(C)]
                row.append(pixel)
            result.append(row)

        return result

    return wrapper


def convert_color_vector(vector):
    c1, c2, c3, color_type = vector

    if color_type == 0:
        R, G, B = c1, c2, c3
        Y = 0.299 * R + 0.587 * G + 0.114 * B
        I = 0.595716 * R - 0.274453 * G - 0.321263 * B
        Q = 0.211456 * R - 0.522591 * G + 0.311135 * B

        return [Y, I, Q, 1]

    elif color_type == 1:
        Y, I, Q = c1, c2, c3

        R = Y + 0.9563 * I + 0.6210 * Q
        G = Y - 0.2721 * I - 0.6474 * Q
        B = Y - 1.1070 * I + 1.7046 * Q

        return [R, G, B, 0]

    else:
        return [0, 0, 0, -1]