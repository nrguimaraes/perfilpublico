
import re
def clear_string(value):
	#value=""
	#for c in string:
	#print('c:'+c)
	#replaced+=dic.get(c,c)
	value = re.sub('à', "a", value)
	value = re.sub('é', "e", value)
	value = re.sub('ã', "a", value)
	value = re.sub('%', "Porc", value)
	value = re.sub('ó', "o", value)
	value = re.sub('í', "i", value)
	value = re.sub('ê', "e", value)
	value = re.sub('ç', "c", value)
	value = re.sub('õ', "o", value)
	value = re.sub('ú', "u", value)
	value = re.sub('á', "a", value)
	#value = re.sub('\`', "", value)
	#value = re.sub('\'', "", value)

	return value


