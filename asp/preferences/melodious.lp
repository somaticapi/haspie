% Possible tendencies are positive, negative and still
pos_tendency(pos;neg;still).

% Music Tendency 
% We can imitate the tendency or not, also we can go against the tendency
tendency(pos,V,B1,B2) :- out_note(V,N1,B1), out_note(V,N2,B2), N1 < N2, beat(B1), beat(B1+1), beat(B2), B1+1==2.
tendency(neg,V,B1,B2) :- out_note(V,N1,B1), out_note(V,N2,B2), N1 > N2, beat(B1), beat(B1+1), beat(B2), B1+1==2.
tendency(still,V,B1,B2) :- out_note(V,N1,B1), out_note(V,N2,B2), N1 == N2, beat(B1), beat(B1+1), beat(B2), B1+1==2.

same_tendency(V1,V2,B1,B2) :- voice(V1), voice(V2), V1 != V2, tendency(T,V1,B1,B2), tendency(T,V2,B1,B2),
							beat(B1), beat(B2), pos_tendency(T). 
cont_tendency(V1,V2,B1,B2) :- voice(V1), voice(V2), V1 != V2, tendency(pos,V1,B1,B2), tendency(neg,V2,B1,B2),
							beat(B1), beat(B2).

% Define the melodic jump between to notes
melodic_jump(V,J,B1,B2) :- out_note(V,N1,B1), out_note(V,N2,B2), (B1+1) == B2, beat(B1+1), J = #abs(N1-N2).

#const melodicjumpw = 1.
#const conttendencyw = 1.
#const sametendencyw = 1.

#const note_errorinstrongp = 7.
#const repeatedgradep = 6.
#const unisonp = 5.
#const melodicjumpp = 4.
#const conttendencyp = 3.
#const sametendencyp = 2.
#const mote_errorinweakp = 1.

#minimize[melodic_jump(_,J,_,_) = (J * melodicjumpw) @ melodicjumpp].
#maximize[cont_tendency(_,_,_,_) = conttendencyw @ conttendencyp].
#maximize[same_tendency(_,_,_,_) = sametendencyw @ sametendencyp].