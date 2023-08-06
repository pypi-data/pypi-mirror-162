"""Distributed Fourier Transform Module."""

import numpy
import itertools

from crocodile.synthesis import (
    fft,
    ifft,
    pad_mid,
    extract_mid,
)

def fmt(x):
    """
    :param x: x

    :return: x
    """
    if x >= 1024 * 1024 and (x % (1024 * 1024)) == 0:
        return "%dM" % (x // 1024 // 1024)
    if x >= 1024 and (x % 1024) == 0:
        return "%dk" % (x // 1024)
    return "%d" % x


def mark_range(
    lbl, x0, x1=None, y0=None, y1=None, ax=None, x_offset=1 / 200, linestyle="--"
):
    """Helper for marking ranges in a graph.

    :param lbl: x
    :param x0: x
    :param x1: x
    :param y1: x
    :param ax: x
    :param x_offset: x
    :param linestyle: linestyle

    """
    if ax is None:
        ax = pylab.gca()
    if y0 is None:
        y0 = ax.get_ylim()[1]
    if y1 is None:
        y1 = ax.get_ylim()[0]
    wdt = ax.get_xlim()[1] - ax.get_xlim()[0]
    ax.add_patch(
        patches.PathPatch(patches.Path([(x0, y0), (x0, y1)]), linestyle=linestyle)
    )
    if x1 is not None:
        ax.add_patch(
            patches.PathPatch(patches.Path([(x1, y0), (x1, y1)]), linestyle=linestyle)
        )
    else:
        x1 = x0
    if pylab.gca().get_yscale() == "linear":
        lbl_y = (y0 * 7 + y1) / 8
    else:
        # Some type of log scale
        lbl_y = (y0 ** 7 * y1) ** (1 / 8)
    ax.annotate(lbl, (x1 + x_offset * wdt, lbl_y))


def find_x_sorted_smooth(xs, ys, y):
    """Find sorted smooth.

    :param xs: x
    :param ys: x
    :param y: x

    :return: xs

    """

    assert len(xs) == len(ys)
    pos = numpy.searchsorted(ys, y)
    if pos <= 0:
        return xs[0]
    if pos >= len(ys) or ys[pos] == ys[pos - 1]:
        return xs[len(ys) - 1]
    w = (y - ys[pos - 1]) / (ys[pos] - ys[pos - 1])
    return xs[pos - 1] * (1 - w) + xs[pos] * w


def find_x_sorted_logsmooth(xs, ys, y):
    """Find sorted log smooth.

    :param xs: x
    :param ys: x
    :param y: x

    :return: log xs

    """
    return find_x_sorted_smooth(xs, numpy.log(numpy.maximum(1e-100, ys)), numpy.log(y))


def whole(xs):
    """."""
    return numpy.all(numpy.abs(xs - numpy.around(xs)) < 1e-13)


def make_subgrid_and_facet(
    G,
    nsubgrid,
    xA_size,
    subgrid_A,
    subgrid_off,
    nfacet,
    yB_size,
    facet_B,
    facet_off,
):
    """

    Calculate the actual subgrids & facets

    :param G: x
    :param nsubgrid: x
    :param xA_size: x
    :param subgrid_A: x
    :param subgrid_off: x
    :param nfacet: x
    :param yB_size: yB_size
    :param facet_B: facet_B
    :param facet_off: facet_off

    :return: subbrig and facet

    """
    FG = fft(G)
    subgrid = numpy.empty((nsubgrid, xA_size), dtype=complex)
    for i in range(nsubgrid):
        subgrid[i] = subgrid_A[i] * extract_mid(numpy.roll(G, -subgrid_off[i]), xA_size)
    facet = numpy.empty((nfacet, yB_size), dtype=complex)
    for j in range(nfacet):
        facet[j] = facet_B[j] * extract_mid(numpy.roll(FG, -facet_off[j]), yB_size)
    return subgrid, facet


def facets_to_subgrid_1(
    facet,
    nsubgrid,
    nfacet,
    xM_yN_size,
    Fb,
    Fn,
    yP_size,
    facet_m0_trunc,
    subgrid_off,
    N,
    xMxN_yP_size,
    xN_yP_size,
    xM_yP_size,
    dtype,
):
    """

    Facet to subgrid 1.

    param facet:
    param nsubgrid:
    param nfacet:
    param xM_yN_size:
    param Fb:
    param Fn:
    param yP_size:
    param facet_m0_trunc:
    param subgrid_off:
    param N:
    param xMxN_yP_size:
    param xN_yP_size:
    param xM_yP_size:
    param dtype:

    return: RNjMiBjFj

    """
    RNjMiBjFj = numpy.empty((nsubgrid, nfacet, xM_yN_size), dtype=dtype)
    for j in range(nfacet):
        BjFj = ifft(pad_mid(facet[j] * Fb, yP_size))
        for i in range(nsubgrid):
            # TODO Seperate into a different function
            MiBjFj = facet_m0_trunc * extract_mid(
                numpy.roll(BjFj, -subgrid_off[i] * yP_size // N), xMxN_yP_size
            )
            MiBjFj_sum = numpy.array(extract_mid(MiBjFj, xM_yP_size))
            MiBjFj_sum[: xN_yP_size // 2] += MiBjFj[-xN_yP_size // 2 :]
            MiBjFj_sum[-xN_yP_size // 2 :] += MiBjFj[: xN_yP_size // 2 :]
            RNjMiBjFj[i, j] = Fn * extract_mid(fft(MiBjFj_sum), xM_yN_size)
    return RNjMiBjFj


def facets_to_subgrid_2(nmbfs, i, xM_size, nfacet, facet_off, N, subgrid_A, xA_size):
    """

    Facet to subgrid 2.
    param nmbfs:
    param i:
    param xM_size:
    param nfacet:
    param facet_off:
    param N:
    param subgrid_A:
    param xA_size:

    return:
    """
    approx = numpy.zeros(xM_size, dtype=complex)
    for j in range(nfacet):
        approx += numpy.roll(pad_mid(nmbfs[i, j], xM_size), facet_off[j] * xM_size // N)
    return subgrid_A[i] * extract_mid(ifft(approx), xA_size)


def subgrid_to_facet_1(
    subgrid, nsubgrid, nfacet, xM_yN_size, xM_size, facet_off, N, Fn
):
    """

    param subgrid:
    param nsubgrid:
    param nfacet:
    param xM_yN_size:
    param xM_size:
    param facet_off:
    param N:
    param Fn:

    return:
    """
    FNjSi = numpy.empty((nsubgrid, nfacet, xM_yN_size), dtype=complex)
    for i in range(nsubgrid):
        FSi = fft(pad_mid(subgrid[i], xM_size))
        for j in range(nfacet):
            FNjSi[i, j] = extract_mid(
                numpy.roll(FSi, -facet_off[j] * xM_size // N), xM_yN_size
            )
    return Fn * FNjSi


def subgrid_to_facet_2(
    nafs,
    j,
    yB_size,
    nsubgrid,
    xMxN_yP_size,
    xM_yP_size,
    xN_yP_size,
    facet_m0_trunc,
    yP_size,
    subgrid_off,
    N,
    Fb,
    facet_B,
):
    """

    param nafs:
    param j:
    param yB_size:
    param nsubgrid:
    param xMxN_yP_size:
    param xM_yP_size:
    param xN_yP_size:
    param facet_m0_trunc:
    param yP_size:
    param subgrid_off:
    param N:
    param Fb:
    param facet_B:

    return:
    """
    approx = numpy.zeros(yB_size, dtype=complex)
    for i in range(nsubgrid):

        #TODO Seperate function
        NjSi = numpy.zeros(xMxN_yP_size, dtype=complex)
        NjSi_mid = extract_mid(NjSi, xM_yP_size)
        NjSi_mid[:] = ifft(
            pad_mid(nafs[i, j], xM_yP_size)
        )  # updates NjSi via reference!
        NjSi[-xN_yP_size // 2 :] = NjSi_mid[: xN_yP_size // 2]
        NjSi[: xN_yP_size // 2 :] = NjSi_mid[-xN_yP_size // 2 :]
        FMiNjSi = fft(
            numpy.roll(
                pad_mid(facet_m0_trunc * NjSi, yP_size), subgrid_off[i] * yP_size // N
            )
        )
        approx += extract_mid(FMiNjSi, yB_size)
    return approx * Fb * facet_B[j]


# Given that the amount of data has been squared, performance is a bit more of a concern now. Fortunately, the entire procedure is completely separable, so let us first re-define the operations to work on one array axis exclusively:
def slice_a(fill_val, axis_val, dims, axis):
    """

    param fill_val:
    param axis_val:
    param dims:
    param axis:

    return:
    """
    return tuple([axis_val if i == axis else fill_val for i in range(dims)])


def pad_mid_a(a, N, axis):
    """

    param a:
    param N:
    param axis:

    return:
    """
    N0 = a.shape[axis]
    if N == N0:
        return a
    pad = slice_a(
        (0, 0), (N // 2 - N0 // 2, (N + 1) // 2 - (N0 + 1) // 2), len(a.shape), axis
    )
    return numpy.pad(a, pad, mode="constant", constant_values=0.0)


def extract_mid_a(a, N, axis):
    """

    param a:
    param N:
    param axis:

    return:
    """
    assert N <= a.shape[axis]
    cx = a.shape[axis] // 2
    if N % 2 != 0:
        slc = slice(cx - N // 2, cx + N // 2 + 1)
    else:
        slc = slice(cx - N // 2, cx + N // 2)
    return a[slice_a(slice(None), slc, len(a.shape), axis)]


def fft_a(a, axis):
    """

    param a:
    param axis:

    return:
    """
    return numpy.fft.fftshift(
        numpy.fft.fft(numpy.fft.ifftshift(a, axis), axis=axis), axis
    )


def ifft_a(a, axis):

    """

    param a:
    param axis:

    return:
    """
    return numpy.fft.fftshift(
        numpy.fft.ifft(numpy.fft.ifftshift(a, axis), axis=axis), axis
    )


def broadcast_a(a, dims, axis):
    """

    param a:
    param dims:
    param axis:

    return:
    """
    slc = [numpy.newaxis] * dims
    slc[axis] = slice(None)
    return a[slc]


def broadcast_a(a, dims, axis):
    """

    param a:
    param dims:
    param axis:
    return:
    """
    return a[slice_a(numpy.newaxis, slice(None), dims, axis)]


# This allows us to define the two fundamental operations - going from $F$ to $b\ast F$ and from $b\ast F$ to $n\ast m(b\ast F)$ separately:


def prepare_facet(facet, axis, Fb, yP_size):
    """

    param facet:
    param axis:
    param Fb:
    param yP_size:
    return:
    """
    BF = pad_mid_a(facet * broadcast_a(Fb, len(facet.shape), axis), yP_size, axis)
    BF = ifft_a(BF, axis)
    return BF


def extract_subgrid(
    BF,
    i,
    axis,
    subgrid_off,
    yP_size,
    xMxN_yP_size,
    facet_m0_trunc,
    xM_yP_size,
    Fn,
    xM_yN_size,
    N,
):
    """

    param BF:
    param i:
    param axis:
    param subgrid_off:
    param yP_size:
    param xMxN_yP_size:
    param facet_m0_trunc:
    param xM_yP_size:
    param Fn:
    param xM_yN_size:
    param N:
    return:
    """
    dims = len(BF.shape)
    BF_mid = extract_mid_a(
        numpy.roll(BF, -subgrid_off[i] * yP_size // N, axis), xMxN_yP_size, axis
    )
    MBF = broadcast_a(facet_m0_trunc, dims, axis) * BF_mid
    MBF_sum = numpy.array(extract_mid_a(MBF, xM_yP_size, axis))
    xN_yP_size = xMxN_yP_size - xM_yP_size
    # [:xN_yP_size//2] / [-xN_yP_size//2:] for axis, [:] otherwise
    slc1 = slice_a(slice(None), slice(xN_yP_size // 2), dims, axis)
    slc2 = slice_a(slice(None), slice(-xN_yP_size // 2, None), dims, axis)
    MBF_sum[slc1] += MBF[slc2]
    MBF_sum[slc2] += MBF[slc1]
    return broadcast_a(Fn, len(BF.shape), axis) * extract_mid_a(
        fft_a(MBF_sum, axis), xM_yN_size, axis
    )


# TODO: Should this be here?
# @interact(xs=(0, N), ys=(0, N))
def test_accuracy(
    nsubgrid,
    xA_size,
    nfacet,
    yB_size,
    N,
    subgrid_off,
    subgrid_A,
    facet_off,
    facet_B,
    xM_yN_size,
    xM_size,
    Fb,
    yP_size,
    xMxN_yP_size,
    facet_m0_trunc,
    xM_yP_size,
    Fn,
    xs=252,
    ys=252,
):
    """

    param nsubgrid:
    param xA_size:
    param nfacet:
    param yB_size:
    param N:
    param subgrid_off:
    param subgrid_A:
    param facet_off:
    param facet_B:
    param xM_yN_size:
    param xM_size:
    param Fb:
    param yP_size:
    param xMxN_yP_size:
    param facet_m0_trunc:
    param xM_yP_size:
    param Fn:
    param xs:
    param ys:
    """
    subgrid_2 = numpy.empty((nsubgrid, nsubgrid, xA_size, xA_size), dtype=complex)
    facet_2 = numpy.empty((nfacet, nfacet, yB_size, yB_size), dtype=complex)

    # G_2 = numpy.exp(2j*numpy.pi*numpy.random.rand(N,N))*numpy.random.rand(N,N)/2
    # FG_2 = fft(G_2)

    FG_2 = numpy.zeros((N, N))
    FG_2[ys, xs] = 1
    G_2 = ifft(FG_2)

    for i0, i1 in itertools.product(range(nsubgrid), range(nsubgrid)):
        subgrid_2[i0, i1] = extract_mid(
            numpy.roll(G_2, (-subgrid_off[i0], -subgrid_off[i1]), (0, 1)), xA_size
        )
        subgrid_2[i0, i1] *= numpy.outer(subgrid_A[i0], subgrid_A[i1])
    for j0, j1 in itertools.product(range(nfacet), range(nfacet)):
        facet_2[j0, j1] = extract_mid(
            numpy.roll(FG_2, (-facet_off[j0], -facet_off[j1]), (0, 1)), yB_size
        )
        facet_2[j0, j1] *= numpy.outer(facet_B[j0], facet_B[j1])

    NMBF_NMBF = numpy.empty(
        (nsubgrid, nsubgrid, nfacet, nfacet, xM_yN_size, xM_yN_size), dtype=complex
    )
    for j0, j1 in itertools.product(range(nfacet), range(nfacet)):
        BF_F = prepare_facet(facet_2[j0, j1], 0, Fb, yP_size)
        BF_BF = prepare_facet(BF_F, 1, Fb, yP_size)
        for i0 in range(nsubgrid):
            NMBF_BF = extract_subgrid(
                BF_BF,
                i0,
                0,
                subgrid_off,
                yP_size,
                xMxN_yP_size,
                facet_m0_trunc,
                xM_yP_size,
                Fn,
                xM_yN_size,
                N,
            )
            for i1 in range(nsubgrid):
                NMBF_NMBF[i0, i1, j0, j1] = extract_subgrid(
                    NMBF_BF,
                    i1,
                    1,
                    subgrid_off,
                    yP_size,
                    xMxN_yP_size,
                    facet_m0_trunc,
                    xM_yP_size,
                    Fn,
                    xM_yN_size,
                    N,
                )

    pylab.rcParams["figure.figsize"] = 16, 8
    err_mean = err_mean_img = 0
    for i0, i1 in itertools.product(range(nsubgrid), range(nsubgrid)):
        approx = numpy.zeros((xM_size, xM_size), dtype=complex)
        for j0, j1 in itertools.product(range(nfacet), range(nfacet)):
            approx += numpy.roll(
                pad_mid(NMBF_NMBF[i0, i1, j0, j1], xM_size),
                (facet_off[j0] * xM_size // N, facet_off[j1] * xM_size // N),
                (0, 1),
            )
        approx = extract_mid(ifft(approx), xA_size)
        approx *= numpy.outer(subgrid_A[i0], subgrid_A[i1])
        err_mean += numpy.abs(approx - subgrid_2[i0, i1]) ** 2 / nsubgrid ** 2
        err_mean_img += numpy.abs(fft(approx - subgrid_2[i0, i1])) ** 2 / nsubgrid ** 2
    # pylab.imshow(numpy.log(numpy.sqrt(err_mean)) / numpy.log(10)); pylab.colorbar(); pylab.show()
    pylab.imshow(numpy.log(numpy.sqrt(err_mean_img)) / numpy.log(10))
    pylab.colorbar()
    pylab.show()
    print(
        "RMSE:",
        numpy.sqrt(numpy.mean(err_mean)),
        "(image:",
        numpy.sqrt(numpy.mean(err_mean_img)),
        ")",
    )