
object run extends App {

  println("Hw0! put any code below to play with the scala")
  println("Hello" + "World")
  println(1+1)
  val x : Int = 10 + 2
  println(x)
  //x = 9 error!!
  var y = 11
  println(y)
  y = 12
  println(y)
  val one = 1
  val kym_ = "KwonYongmin"
  println(s"${one} ${kym_}")

  //scala is statically type language and there is no type error

  //Multi-line Expressions
  val a1 = {
    val b = 2 + 3
    b + 4
  } 
  println(a1)

  // function
  val add = (x: Int, y:Int) => x+y
  println(add(1, 2))

  // method
  def mul(x: Int, y: Int) : Int = x*y
  println(mul(5, 9))

  // class
  class Account(id: Int, owner: String){
  def ShowAccountInfo(): Unit=
    println(s"ID: ${id}, OWNER: ${owner}")
  }

  val acc1 = new Account(115, "Yongmin")
  acc1.ShowAccountInfo() // no need to overload operator == for new class


  // object: Globally accessible if defined outside any other classes
  object IdFactory{
    private var counter = 0
    def create(): Int = {
      counter += 1
      counter
    }
  }

  class Account2(owner: String){
    private val id2 :Int = IdFactory.create()
    def ShowAccount2Info(): Unit=
      println(s"ID: ${id2}, OWNER: ${owner}")
  }

  val acc2_1 = new Account2("Chulsoo")
  acc2_1.ShowAccount2Info()
  val acc2_2 = new Account2("YongYong")
  acc2_2.ShowAccount2Info()

  // trait: abstract class in C++ (cannot be instatiated)
  trait Person{
    var name = " "
    def ShowPersonalInfo(): Unit = {
      println(s"Name: ${name}")
    }
  }

  class student(sn: String, m: String) extends Person {
    name = sn
    val major = m
    def ShowStudentInfo(): Unit = {
      ShowPersonalInfo()
      println(s"Major: ${major}")
    }
  }

  val kym = new student("YongminKwon", "ComputerScience")
  kym.ShowStudentInfo()

  // Entry Point: the point where the program starts its execution from
  // object Main extends App {...}
  // object Main { def main(args: Array[String]) : Unit ={...} }\

  // Conditional Expression
  val fact: Int => Int = (x: Int) => {
    if (x==1) x
    else x*fact(x-1)
  }
  // Why "=> Int" ??

  // List: immutable
  val emp = List()
  val t = List(1, 2)
  // type of elements is no matter
  // var: updates whole list

  // Tuples
  val tuple = ("number", 1)
  val ffff = tuple._1
  val ssss = tuple._2
  println(s"${ffff} ${ssss}")

  // Maps: immutable
  val a = Map("CEO"->"John", "CFO"->"Mary")
  println(a("CEO"))

  //HashMap
  import scala.collection.mutable.HashMap
  var hashmap = HashMap("Yongmin" -> "RB", "Jongah" -> "LDM", "Gyohun"->"LCB")
  println(hashmap)
  println(hashmap("Yongmin"))
  hashmap += ("hyunki"->"WF")
  println(hashmap)
  println(hashmap.apply("Jongah"))

  var hash = new HashMap[String, String]
  hash += ("Yongmin"->"DHE")
  hash += ("JinYoung"->"ECE")
  println(hash)
  hash -= "Yongmin"
  println(hash)

  sealed trait IntList
  // sealed : the something outside of file cannot extend this trait
  case class Nil() extends IntList
  case class Cons(h: Int, t: IntList) extends IntList

  val n0 = Nil()
  val l0 = Cons(10, Cons(9, Nil()))
  println(n0.isInstanceOf[IntList])
  println(n0.isInstanceOf[Nil])
  println(n0.isInstanceOf[Cons])
  println(l0)
  println(l0.isInstanceOf[Cons])
  println(l0.isInstanceOf[IntList])
  println(l0.isInstanceOf[Nil])

  sealed trait MyList[A]
  case class Nil_1() extends MyList[Any]//Any??
  case class Cons_1[A](h: A, t: MyList[A]) extends MyList[A]

  val n1 = Nil_1()
  val int_list = Cons_1(1,Cons_1(2, Cons_1(3, Nil_1())))
  val string_list = Cons_1("Kwon", Cons_1("Kim", Nil_1()))
  println(int_list)
  println(string_list)

  //pattern matching
  def sum(l: IntList): Int = l match{
    case Cons(h, t) => h+sum(t)
    case Nil() => 0
  }

  println(sum(Cons(1,Cons(2,Cons(3, Nil())))))

  def sum2(l: IntList): Int = l match{
    case c: Cons => c.h + sum(c.t)
    case _ => 0
  }

  println(sum2(Cons(1,Cons(2,Cons(3, Nil())))))

  // Functional programming
  // a paradigm => Other examples: imperative, OOP, AOP, etc
  // rreat computations as mathematical functions =< work with immutable data
  // construct programs with only pure functions(no side effect => no change the value by ref)

  // The advantage of such immutability
  // easy to comprehend the other's code
  // okay to assume that the value remains intact

  // Needs for recursion 
  // in functional programming, loops are useless
  // One should use recursion to implement the program repeating the same computation

  // recursive problem 
  def sum_r(num: Int): Int ={
    if(num == 0)
      0
    else
      num + sum_r(num-1)
  }

  println(sum_r(10))

  val n3 = Nil()
  val l3 = Cons(10,Cons(9, Nil()))

  //ex1 list length
  def length(li: IntList) : Int ={
    li match {
      case Nil() => 0
      case Cons(h,t) => 1+length(t)
    }
  }

  println(length(l3))

  //ex2 list concatnation
  def concat(fst: IntList, snd: IntList): IntList = {
    fst match {
      case Nil() => snd
      case Cons(h,t) => Cons(h, concat(t,snd))
    }
  }
  val m3 = Cons(8, Cons(7, Nil()))
  println(concat(l3, m3))

  //ex3 list reverse
  def reverse(li: IntList): IntList = {
    li match {
      case Nil() => li
      case Cons(h, t) => concat(reverse(t), Cons(h, Nil()))
    }
  }
  val o3 = concat(l3, m3)
  println(reverse(o3))

  val cube = (x: Int) => x * x * x
  (x: Int, y: Int, z: Int) => cube(x) + cube(y) + cube(z)
  val square = (x: Int) => x * x
  (x: Int, y: Int, z: Int) => square(x) + square(y) + square(z)
  val sum3 = (x: Int, y:Int, z: Int, ftn: Int => Int) =>
  ftn(x) + ftn(y) + ftn(z)
  println(sum3(1,2,3,cube)) // prints 36
  println(sum3(1,2,3,square)) // prints 14

  val l = Cons(5, Cons(3, Cons(7, Nil())))
  def map (ftn: Int => Int, li: IntList): IntList =
    li match {
      case Nil() => Nil()
      case Cons(h,t) => Cons(ftn(h), map(ftn,t))
    }
  println(map(cube,l))// prints Cons(125,Cons(27,Cons(343,Nil())))

  def mult (a: Int, b:Int) = a * b
  def fold (base: Int, ftn: (Int,Int) => Int, li: IntList): Int =
    li match {
      case Nil() => base
      case Cons(h,t) => fold(ftn(base,h),ftn,t)
    }
  println(fold(1,mult,l)) // prints 105


  // Anonymous Functions
  val b_A = List(1, 2, 3)
  val a_A = b_A.map((t) => t + 1)
  println(a_A)

  // Closure
  def makeAdder(x: Int): Int => Int = {
    def adder(y: Int): Int = x + y
      adder
  }
  val add1 = makeAdder(1)
  println(add1(2)) // prints 2
  val add2 = makeAdder(2)
  println(add2(2)) // prints 3

  // Option Types
  trait OptionalInt
  case object None extends OptionalInt
  case class Some(n: Int) extends OptionalInt
  def nth(li: IntList, n: Int): OptionalInt =
    li match {
      case Nil() => None
      case Cons(h,t) => if(n == 0) Some(h) else nth(t,n-1)
    }
  val l2 = Cons(0, Cons(3, Nil()))
  println(nth(l2,0)) // prints Some(3)
  println(nth(l2,10)) // prints None

}



