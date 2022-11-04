^class FirstClass {
   integer_1 : Int <- 0;
   integer_2 : Int <- 0;
   integer_2 : Int <- 0;
   testout : Int;

   value() : Int { integer_1 };
};

class SecondClass inherits IO {
   integer_2 : Int <- 0;
   testFunction(firstNumber : Int, second: Int) : Int {
      (
      let test : Int in
	 {
	        -- should always be zero
            test_non_existent <- firstNumber - firstNumber;
	 }
      )
   };

};

class Main {
   
   unused_declaration : Sting;
   my_variable : FirstClass;
    int: Int <- 0;
   main() : Object {
      {
           my_variable <- (new SecondClass);

      }
   };

};

class Dude {};
