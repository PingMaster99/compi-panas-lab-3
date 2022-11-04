class FirstClass {
   integer_1 : Int <- 0;
   integer_2 : Int <- 0;
   testout : Int;

   value() : Int { integer_1 };
};

class SecondClass inherits IO {
   integer_2 : Int <- 0;
   test : String;
   testFunction(firstNumber : Int, second: Int) : IO {
      (
      let test : Int in
	 {
	        -- should always be zero
            test <- firstNumber - firstNumber;
            out_int(test);
	 }
      )
   };

};

class Main {
   
   unused_declaration : String;
   my_variable : SecondClass;
    int: Int <- 0;
   main() : Object {
      {
           my_variable <- (new SecondClass);
           my_variable.testFunction(2, 3);
      }
   };

};

class Dude {};
