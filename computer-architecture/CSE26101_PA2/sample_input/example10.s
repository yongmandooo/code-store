	.data
data1:	.word   1
data2:	.word   10
	.text
main:
	add	$3, $0, -1
	sltiu	$2, $3, 1
	addiu	$5, $0, -24
	sltiu	$6, $5, 20
	sltiu	$7, $0, -1
	sltiu	$8, $0, 1