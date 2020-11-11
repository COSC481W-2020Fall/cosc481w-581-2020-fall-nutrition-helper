from decimal import Decimal

# for display purposes
# chops off extra zeros if unnecessary
def chop_zeros(value):
	if value == 0:
		return Decimal('0')
	elif value == value.to_integral():
		return value.quantize(Decimal(1))
	else:
		return value.normalize()