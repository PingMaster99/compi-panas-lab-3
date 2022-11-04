(*
* Arithmetic test for PanaCompiler
* Bool can be added or subtracted with ints
*
*)


class Dude {};
class Main{

    -- int
    int_a : Int <- 2;
    int_b : Int <- 5;

    -- bool
    bool_a : Bool <- true;
    bool_b: Bool <- false;

    -- string
    string_a: String <- "Python";
    string_b: String <- "Compilers";

    main() : SELF_TYPE {
	{
	    int_a <- 3+2;
        int_b <- int_b / int_a;                         -- division
        int_a <- int_b - bool_b;                        -- boolean casting
        string_a <- string_a  + string_b;               -- strings
        int_a <- 0 * 1;
        self;
	}
    };
};