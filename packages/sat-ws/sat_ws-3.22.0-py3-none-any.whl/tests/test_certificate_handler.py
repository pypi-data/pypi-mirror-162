# pylint: disable=redefined-outer-name
class FakeSignature:
    data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    signature = "afxUybh/NrIf4LTFrOT22wS3mjdurwx6J1gNlYSkNbcmt9NF1jDyw1oT3Akk17bsLUeyH+JQkiiiydW2Tpi4xmKt1X5JjzVu/zDu/u8R910nn7ZRdVACT95pGuKTa74NoDNW9eX2IruQK8X7TmSHasiESTdzmKZNuLE5VTn2c9O5XQmJUCxSV5oieWHyI02OKJu7D60cT/Ma+yDFPuOSc6pnCY71QH21X3rNS8GBHfkgNaC2HA6BpNUGrxTBkcpvTvdyXgPyffwWKQjGyWdRNctnJUy21O6mEJmz6evs93/CAGAaLWvv7Q4e+CeaT63hQiVWxjTKY+BN7Uc4b2KgTQ=="
    bad_signature = "InvalidSignature"


def test_sign(certificate_handler):
    assert certificate_handler.sign(FakeSignature.data) == FakeSignature.signature


def test_sign_invalid(certificate_handler):
    assert certificate_handler.sign(FakeSignature.data) != FakeSignature.bad_signature
