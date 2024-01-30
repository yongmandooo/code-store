   .data
   .text
main:
   move   $8, $9
   blt   $8, $9, lab1
   push   $8
lab1:
   pop   $8