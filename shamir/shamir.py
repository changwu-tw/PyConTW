import hmac
from random import randint, shuffle

"""ShareOverhead is the byte size overhead of each share
when using Split on a secret. This is caused by appending
a one byte tag to the share."""
ShareOverhead = 1


def precompute_exp_log():
    exp = [0 for i in range(255)]
    log = [0 for i in range(256)]

    poly = 1
    for i in range(255):
        exp[i] = poly
        log[poly] = i

        # Multiply poly by the polynomial x + 1.
        poly = (poly << 1) ^ poly

        # Reduce poly by x^8 + x^4 + x^3 + x + 1.
        if poly & 0x100:
            poly ^= 0x11B

    return exp, log


EXP_TABLE, LOG_TABLE = precompute_exp_log()


# makePolynomial constructs a random polynomial of the given
# degree but with the provided intercept value.
def make_polynomial(intercept, degree):
    # Assign random co-efficients to the polynomial
    # a_0, a_1, ... a_n
    coefficients = [randint(1, 255) for _ in range(degree)]

    # Ensure the intercept is set
    return [intercept] + coefficients


# evaluate returns the value of the polynomial for the given x
def evaluate(poly, x):
    # Special case the origin
    if x == 0:
        return poly[0]

    # Compute the polynomial value using Horner's method.
    degree = len(poly) - 1
    out = poly[degree]
    for i in range(degree - 1, -1, -1):
        coeff = poly[i]
        out = add(mult(out, x), coeff)

    return out


# interpolatePolynomial takes N sample points and returns
# the value at a given x using a lagrange interpolation.
def interpolate_polynomial(x_samples, y_samples, x):
    limit = len(x_samples)
    result = 0

    # https://en.wikipedia.org/wiki/Polynomial_interpolation
    for i in range(limit):
        basis = 1
        for j in range(limit):
            if i != j:
                num = add(x, x_samples[j])
                denom = add(x_samples[i], x_samples[j])
                term = div(num, denom)
                basis = mult(basis, term)
        group = mult(y_samples[i], basis)
        result = add(result, group)

    return result


# div divides two numbers in GF(2^8)
def div(a, b):
    if b == 0:
        # leaks some timing information but we don't care anyways as this
        # should never happen, hence the panic
        raise ZeroDivisionError("divide by zero")

    zero = 0
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]

    diff = (int(log_a) - int(log_b)) % 255
    assert 255 > diff >= 0, "shamir error: diff < 0"

    ret = EXP_TABLE[diff]

    # Ensure we return zero if a is zero but aren't subject to timing attacks
    if hmac.compare_digest(bytes(a), bytes(0)):
        ret = zero

    return ret


# mult multiplies two numbers in GF(2^8)
def mult(a, b):
    zero = 0
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    sum = (int(log_a) + int(log_b)) % 255

    ret = EXP_TABLE[sum]

    # Ensure we return zero if either a or b are zero but aren't subject to
    # timing attacks
    if hmac.compare_digest(bytes(a), bytes(0)):
        ret = zero
    elif hmac.compare_digest(bytes(b), bytes(0)):
        ret = zero

    return ret


# add combines two numbers in GF(2^8)
# This can also be used for subtraction since it is symmetric.
def add(a, b):
    return a ^ b


# split takes an arbitrarily long secret and generates a `parts`
# number of shares, `threshold` of which are required to reconstruct
# the secret. The parts and threshold must be at least 2, and less
# than 256. The returned shares are each one byte longer than the secret
# as they attach a tag used to reconstruct the secret.
def split(secret, parts, threshold):
    # Sanity check the input
    if parts < threshold:
        raise Exception("parts cannot be less than threshold")

    if parts > 255:
        raise Exception("parts cannot exceed 255")

    if threshold < 2:
        raise Exception("threshold must be at least 2")

    assert threshold <= 255, "threshold cannot exceed 255"

    if secret is None or len(secret) == 0:
        raise Exception("cannot split an empty secret")

    # Generate random list of x coordinates
    xCoordinates = [i for i in range(255)]
    shuffle(xCoordinates)

    # Allocate the output array, initialize the final byte
    # of the output with the offset. The representation of each
    # output is {y1, y2, .., yN, x}.
    out = [None] * parts
    for i in range(len(out)):
        out[i] = [None] * len(secret)
        out[i] += [xCoordinates[i] + 1]

    # Construct a random polynomial for each byte of the secret.
    # Because we are using a field of size 256, we can only represent
    # a single byte as the intercept of the polynomial, so we must
    # use a new polynomial for each byte.
    for idx, val in enumerate(secret):
        p = make_polynomial(val, threshold - 1)

        # Generate a `parts` number of (x,y) pairs
        # We cheat by encoding the x value once as the final index,
        # so that it only needs to be stored once.
        for i in range(parts):
            x = xCoordinates[i] + 1
            y = evaluate(p, x)
            out[i][idx] = y

    # Return the encoded secrets
    return out


# combine is used to reverse a Split and reconstruct a secret
# once a `threshold` number of parts are available.
def combine(parts):
    # Verify enough parts provided
    if parts is None or len(parts) < 2:
        raise Exception("less than two parts cannot be used to reconstruct the secret")

    # Verify the parts are all the same length
    first_part_len = len(parts[0])
    if first_part_len < 2:
        raise Exception("parts must be at least two bytes")

    for i, _ in enumerate(parts):
        if len(parts[i]) != first_part_len:
            raise Exception("all parts must be the same length")

    # Create a buffer to store the reconstructed secret
    secret = [None] * (first_part_len - 1)

    # Buffer to store the samples
    x_samples = [None] * len(parts)
    y_samples = [None] * len(parts)

    # Set the x value for each sample and ensure no x_sample values are the same,
    # otherwise div() can be unhappy
    checkmap = {}
    for i, part in enumerate(parts):
        samp = part[first_part_len - 1]
        if samp in checkmap.keys():
            raise Exception("duplicate part detected")
        checkmap[samp] = True
        x_samples[i] = samp

    # Reconstruct each byte
    for idx, _ in enumerate(secret):
        # Set the y value for each sample
        for i, part in enumerate(parts):
            y_samples[i] = part[idx]

        # Interpolate the polynomial and compute the value at 0
        val = interpolate_polynomial(x_samples, y_samples, 0)

        # Evaluate the 0th value to get the intercept
        secret[idx] = int(round(val))

    return bytes(secret)
