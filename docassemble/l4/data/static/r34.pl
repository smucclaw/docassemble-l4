% An implementation of Logic Programming with Defaults and Argumentation Theories

% These are the three predicates that the user should use in their code.
% they can also be customized to be displayed in a more friendly way, as can the
% other predicates. For example, to improve the display you can encode
% #pred according_to(R,flies(X)) :: 'according to rule @(R), @(X) flies'.
#pred rule(R) :: '@(R) is a rule'.
#pred conclusion(C) :: '@(C) is a conclusion'.
%#pred according_to(R,C) :: 'according to rule @(R), the conclusion @(C) holds'.
#pred overrides(R1,C1,R2,C2) :: 'the conclusion @(C1) from rule @(R1) overrides the conclusion @(C2) from rule @(R2)'.
#pred opposes(R1,C1,R2,C2) :: 'the conclusion @(C1) from rule @(R1) conflicts with the conclusion @(C2) from rule @(R2)'.

% Oppositions must be stated explicitly, and must be ground at evaluation time.
opposes(R1,C1,R2,C2) :- opposes(R2,C2,R1,C1).

% A rule is rebutted if it conflicts with another rule, neither is refuted, the rebutting rule is not compromised, and there is no priority between them.
#pred rebutted_by(R1,C1,R2,C2) :: 'the conclusion @(C1) from rule @(R1) is rebutted by the conclusion @(C2) from rule @(R2)'.

rebutted_by(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    according_to(Rule,Conclusion),
    according_to(Other_Rule,Other_Conclusion),
    opposes(Rule,Conclusion,Other_Rule,Other_Conclusion),
    not refuted(Rule,Conclusion),
    not refuted(Other_Rule,Other_Conclusion),
    not compromised(Other_Rule,Other_Conclusion),
    not overrides(Rule,Conclusion,Other_Rule,Other_Conclusion),
    not overrides(Other_Rule,Other_Conclusion,Rule,Conclusion).

% A rule is refuted if there is another rule that conflicts with it and overrides it.
#pred refuted_by(R1,C1,R2,C2) :: 'the conclusion @(C1) from rule @(R1) is refuted by the conclusion @(C2) from rule @(R2)'.
refuted_by(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    opposes(Rule,Conclusion,Other_Rule,Other_Conclusion),
    overrides(Other_Rule,Other_Conclusion,Rule,Conclusion),
    according_to(Rule,Conclusion),
    Rule \= Other_Rule,
    Conclusion \= Other_Conclusion,
    according_to(Other_Rule,Other_Conclusion).

% A rule is compromised if it is either refuted or defeated.
#pred compromised(Rule,Conclusion) :: 'the conclusion @(Conclusion) from rule @(Rule) is compromised'.

compromised(Rule,Conclusion) :-
    refuted_by(Rule,Conclusion,_,_).

%% Inserting this rule causes OLON problems.
compromised(Rule,Conclusion) :-
    defeated_by(Rule,Conclusion).

% A rule is disqualified if it defeats itself through a cycle of rebuttals or refutations (not disqualifications)
#pred defeated_by_closure(R1,C1,R2,C2) :: 'the conclusion @(C1) from rule @(R1) is defeated by closure by the conclusion @(C2) from rule @(R2)'.
#pred defeated_by_closure(R,C,R,C) :: 'the conclusion @(C1) from rule @(R1) is self-defeating'.

defeated_by_closure(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    unsafe_rebutted_by(Rule,Conclusion,Other_Rule,Other_Conclusion).
defeated_by_closure(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    refuted_by(Rule,Conclusion,Other_Rule,Other_Conclusion).
defeated_by_closure(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    unsafe_rebutted_by(Rule,Conclusion,Third_Rule,Third_Conclusion),
    defeated_by_closure(Third_Rule,Third_Conclusion,Other_Rule,Other_Conclusion).
defeated_by_closure(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    refuted_by(Rule,Conclusion,Third_Rule,Third_Conclusion),
    defeated_by_closure(Third_Rule,Third_Conclusion,Other_Rule,Other_Conclusion).

% Defeat by closure checks for chains of rebuttals and refutations, regardless of whether
% the defeating or rebutting rule is defeated or compromised.
unsafe_rebutted_by(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    according_to(Rule,Conclusion),
    according_to(Other_Rule,Other_Conclusion),
    opposes(Rule,Conclusion,Other_Rule,Other_Conclusion),
    not overrides(Rule,Conclusion,Other_Rule,Other_Conclusion),
    not overrides(Other_Rule,Other_Conclusion,Rule,Conclusion).

#pred disqualified(Rule,Conclusion) :: 'the conclusion @(Conclusion) from rule @(Rule) is disqualified'.

disqualified(Rule,Conclusion) :-
    defeated_by_closure(Rule,Conclusion,Rule,Conclusion).

% A rule is defeated if it is refuted or rebutted by a rule that is not compromised, or if it is disqualified.
% (A rebutting rule is already not compromsied, the requirement of non-compromise does not apply to refutation)
%#pred defeated(Rule,Conclusion) :: 'the conclusion @(Conclusion) from rule @(Rule) is defeated'.
#pred defeated_by_disqualification(R1,C1,R2,C2) :: 'the conclusion @(C1) from rule @(R1) is defeated by disqualification by the conclusion @(C2) from rule @(R2)'.
#pred defeated_by_rebuttal(R,C,OR,OC) :: 'the conclusion @(C) from rule @(R) is defeated by rebuttal by the conclusion @(OC) from rule @(R)'.
#pred defeated_by_refutation(R,C,OR,OC) :: 'the conclusion @(C) from rule @(R) is defeated by refutation by the conclusion @(OC) from rule @(R)'.

defeated_by_disqualification(Rule,Conclusion,Rule,Conclusion) :- disqualified(Rule,Conclusion).

defeated_by_rebuttal(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    Rule \= Other_Rule,
    Conclusion \= Other_Conclusion,
    rebutted_by(Rule,Conclusion,Other_Rule,Other_Conclusion).

% The ordering of the clauses in the body seems important for whether or not an OLON situation is created.
defeated_by_refutation(Rule,Conclusion,Other_Rule,Other_Conclusion) :-
    refuted_by(Rule,Conclusion,Other_Rule,Other_Conclusion).

% A conclusion can be defeated three ways.
defeated(R,C) :-
    R \= OR,
    C \= OC,
    opposes(R,C,OR,OC),
    defeated_by_disqualification(R,C,OR,OC).
defeated(R,C) :-
    R \= OR,
    C \= OC,
    opposes(R,C,OR,OC),
    defeated_by_rebuttal(R,C,OR,OC).
defeated(R,C) :-
    R \= OR,
    C \= OC,
    opposes(R,C,OR,OC),
    defeated_by_refutation(R,C,OR,OC).

% a conclusion holds if it is found and not defeated.
%#pred legally_holds(R,C) :: 'the conclusion @(C) from rule @(R) ultimately holds'.
legally_holds(R,C) :-
    not defeated(R,C),
    according_to(R,C).





#pred legally_holds(Rule,may(Y,accept,Z)) :: 'it holds in accordance with {@(Rule)} that @(Y) is permitted to accept @(Z)'.
#pred legally_holds(Rule,must_not(Y,accept,Z)) :: 'it holds in accordance with {@(Rule)} that @(Y) is prohibited from accepting @(Z)'.
#pred defeated(Rule,may(Y,accept,Z)) :: 'the conclusion that @(Y) may accept @(Z) from rule {@(Rule)} is defeated'.
#pred defeated(Rule,must_not(Y,accept,Z)) :: 'the conclusion that @(Y) must not accept @(Z) from rule {@(Rule)} is defeated'.

% PREDICATE DEFINITIONS
#pred accepts_position_as_representative(A,B,C) :: '@(A) accepts the position @(B) as a representative of @(C)'.
#pred according_to(X,described_in_s1(Y)) :: 'according to {@(X)}, @(Y) is described in section 1'.
#pred according_to(X,may(Y,accept,Z)) :: 'in accordance with {@(X)}, @(Y) is permitted to accept @(Z)'.
#pred according_to(X,must_not(Y,accept,Z)) :: 'in accordance with {@(X)}, @(Y) is prohibited from accepting @(Z)'.
#pred as_compensation_for(A,B) :: '@(A) is provided as compensation in respect of @(B)'.
#pred associated_with(A,B) :: '@(A) is associated with @(B)'.
#pred beneficial_owner_of(X,Y) :: '@(X) is a beneficial owner of @(Y)'.
#pred business_entity(X) :: 'in accordance with the {business entity|r34(9) definition of business entity}, @(X) is a business entity'.
#pred business_trust(X) :: '@(X) is a business trust'.
#pred business(X) :: ' in accordance with the {business|r34(9) definition of business}, @(X) is a business'.
#pred calling(X) :: '@(X) is a calling'.
#pred carries_on(X,Y) :: '@(X) carries on @(Y)'.
#pred company(X) :: '@(X) is a company'.
#pred conditions_of_second_schedule_satisfied :: 'the conditions of the second schedule are satisfied'.
#pred corporation(X) :: '@(X) is a corporation'.
%#pred defeated(X,Y) :: 'the conclusion from @(X) of @(Y) is defeated'.
#pred derogates_from_dignity_of_legal_profession(X) :: '@(X) derogates from the dignity of the legal profession'.
#pred described_in_first_schedule(X) :: '@(X) is set out in the first schedule'.
#pred described_in_s1(B) :: '@(B) is a business described in 34(1)'.
#pred detracts_from_dignity_of_legal_profession(X) :: '@(X) detracts from the dignity of the legal profession'.
#pred director_of(X,Y) :: '@(X) is a director of @(Y)'.
#pred entitles_holder(X) :: '@(X) entitles the holder to perform executive functions'.
#pred -executive_appointment(X) :: '@(X) is not an executive appointment for the purposes of section 34'.
#pred executive_appointment(X) :: 'in accordance with the {executive appointment|r34(9) definition of executive appointment}, @(X) is an executive appointment'.
#pred executive_appointment_associated_with_a_business(X,Y) :: '@(X) is an executive appointment associated with the business @(Y)'.
#pred executive_appointment_in_a_business_entity(X,Y) :: '@(X) is an executive appointment in the business entity @(Y)'.
#pred executive_appointment_in_a_law_practice(X,Y) :: '@(X) is an executive appointment in the law practice @(Y)'.
#pred -for_profit(X) :: '@(X) is not for profit'.
#pred for_profit(X) :: '@(X) is for profit'.
#pred foreign_law_practice(X) :: '@(X) is a foreign law practice'.
#pred formal_law_alliance(X) :: '@(X) is a formal law alliance'.
#pred in_fourth_schedule(X) :: '@(X) is listed in the fourth schedule'.
#pred in_third_schedule(X) :: '@(X) is listed in the third schedule'.
#pred in(X,Y) :: '@(X) is in @(Y)'.
#pred incompatible_dignity_of_legal_profession(X) :: '@(X) is incompatible with the dignity of the legal profession'.
#pred independent_director(X) :: '@(X) is an independent directorship'.
#pred institution(X) :: '@(X) is an institution'.
#pred involves_paying_commission(X,Y,Z) :: '@(X) involves paying @(Y) to @(Z)'.
#pred involves_sharing_fees(X,Y,Z) :: '@(X) involves sharing @(Y) with @(Z)'.
#pred joint_law_venture(X) :: '@(X) is a joint law venture'.
#pred jurisdiction(X,Y) :: '@(X) is located in @(Y)'.
#pred law_practice_in_singapore(X) :: '@(X) is a singapore law practice'.
#pred law_practice(X) :: '@(X) is a law practice'.
#pred law_related_service(X) :: '@(X) is a law-related service'.
#pred legal_owner_of(X,Y) :: '@(X) is a legal owner of @(Y)'.
#pred legal_practitioner(X) :: '@(X) is a legal practitioner'.
#pred legal_service(X) :: '@(X) is a legal service'.
#pred legal_work(X) :: '@(X) is legal work'.
#pred llp(X) :: '@(X) is a limited liability partnership'.
#pred locum_solicitor(X) :: '@(X) is a locum solicitor'.
#pred materially_interferes_with(X,Y,Z) :: '@(X) materially interferes with @(Y) with regard to @(Z)'.
#pred may(A,accept,B) :: '@(A) may accept an appoinment to @(B)'.
#pred member_of(A,B) :: '@(A) is a member of @(B)'.
#pred must_not(A,accept,B) :: '@(A) must not accept @(B)'.
#pred must_not(A,participate,B) :: '@(A) is prohibited from participating in @(B)'.
#pred non_executive_director(X) :: '@(X) is a non-executive directorship'.
#pred owner_and_not_partner_of(Y,Z) :: 'someone who is a legal or beneficial owner of @(Y) is not a sole proprietor, partner, or director of @(Z)'.
#pred owner_of(X,Y) :: '@(X) is the legal or beneficial owner of @(Y)'.
#pred participation_prohibited(X,Y) :: '@(X) is prohibited from participating in @(Y)'.
#pred partner_of(X,Y) :: '@(X) is a partner of @(Y)'.
#pred partner_sp_or_director_of(X,Y) :: '@(X) is a partner, sole proprietor, or director of @(Y)'.
#pred partnership(X) :: '@(X) is a partnership'.
#pred performed_by(A,B) :: '@(A) was performed by @(B)'.
#pred position(X) :: '@(X) is a position'.
#pred primary_occupation_of(X,Y) :: '@(Y) is the primary occupation of @(X)'.
#pred prohibited_business(X) :: '@(X) is a prohibited business'.
#pred provides_legal_or_law_related_services(X) :: '@(X) provides legal or law-related services'.
#pred provides(A,B) :: '@(A) provides @(B)'.
#pred service(X) :: '@(X) is a service'.
#pred sole_proprietor_of(X,Y) :: '@(X) is the sole proprietor of @(Y)'.
#pred soleprop(X) :: '@(X) is a sole proprietorship'.
#pred third_schedule_institution(X) :: '@(X) is an institution listed in the third schedule'.
#pred trade(X) :: '@(X) is a trade'.
#pred unauthorized(X) :: '@(X) is unauthorised to peform legal work'.
#pred unfair(X) :: '@(X) is likely to unfairly attract business in the practice of law'.

% RULE 34
% 34. Executive appointments

% RULE 34(1)
% 34.—(1)  A legal practitioner must not accept any executive appointment associated with 
% any of the following businesses:

according_to(r34_1,must_not(Actor, accept, Appointment)) :-
    legal_practitioner(Actor),
    associated_with(Appointment,Business),
    business(Business),
    according_to(Rule,described_in_s1(Business)),
    executive_appointment(Appointment). % moving executive appointment to the bottom of the list of clauses made the code run.

% (a)	any business which detracts from, is incompatible with, or derogates from the dignity of,
% the legal profession;


according_to(r34_1_a,described_in_s1(Business)) :-
    detracts_from_dignity_of_legal_profession(Business),
    business(Business).
according_to(r34_1_a,described_in_s1(Business)) :-
    incompatible_dignity_of_legal_profession(Business),
    business(Business).
according_to(r34_1_a,described_in_s1(Business)) :- 
    derogates_from_dignity_of_legal_profession(Business),
    business(Business).

% (b) Repealed in amendment.

% (c)	any business which is likely to unfairly attract business in the practice of law;


according_to(r34_1_c,described_in_s1(X)) :- unfair(X).

% (d)	any business which involves the sharing of the legal practitioner’s fees with, 
% or the payment of a commission to, any unauthorised person for legal work performed 
% by the legal practitioner;


according_to(r34_1_d,described_in_s1(X)) :- involves_sharing_fees(X,Fees,Recipient), as_compensation_for(Fees,Work), performed_by(Work,Lawyer), legal_work(Work), unauthorized(Recipient).
according_to(r34_1_d,described_in_s1(X)) :- involves_paying_commission(X,Fees,Recipient), as_compensation_for(Fees,Work), performed_by(Work,Lawyer), legal_work(Work), unauthorized(Recipient).


% (e)	any business set out in the First Schedule;

according_to(r34_1_e,described_in_s1(X)) :- described_in_first_schedule(X).

% (f)	any business which is prohibited by —
% (i)	the Act;
% (ii)	these Rules or any other subsidiary legislation made under the Act;
% (iii)	any practice directions, guidance notes and rulings issued under section 71(6) of the Act; or
% (iv)	any practice directions, guidance notes and rulings (relating to professional practice,
%  etiquette, conduct and discipline) issued by the Council or the Society.

according_to(r34_1_f,described_in_s1(X)) :- prohibited_business(X).

% AMENDED RULE 34(1A)
% 1A: A legal practitioner must not accept any executive appointment that:
% materially interferes with —
% (i)	the legal practitioner’s primary occupation of practising as a lawyer;
% (ii)	the legal practitioner’s availability to those who may seek the legal practitioner’s 
% services as a lawyer; or
% (iii)	the representation of the legal practitioner’s clients.

%% NOTE: In the legislative text, the numbering would be different. In the code, the number of
%% the section is left as r34_1_b solely so that we do not need to rewrite the tests in order
%% for them to work.

according_to(r34_1_b,must_not(Actor, accept, Appointment)) :-
    legal_practitioner(Actor),
    executive_appointment(Appointment),
    materially_interferes_with(Appointment,practicing_as_a_lawyer,Actor),
    primary_occupation_of(Actor,practicing_as_a_lawyer).

according_to(r34_1_b,must_not(Actor, accept, Appointment)) :-
    legal_practitioner(Actor),
    executive_appointment(Appointment),
    materially_interferes_with(Appointment,availability,Actor).

according_to(r34_1_b,must_not(Actor, accept, Appointment)) :-
    legal_practitioner(Actor),
    executive_appointment(Appointment),
    materially_interferes_with(Appointment,representation,Actor).

% RULE 34(2)(a)
% (2)  Subject to paragraph (1), a legal practitioner in a Singapore law practice 
% (called in this paragraph the main practice) may accept an executive appointment 
% in another Singapore law practice (called in this paragraph the related practice), 
% if the related practice is connected to the main practice in either of the following ways:
% (a)	every legal or beneficial owner of the related practice is the sole proprietor, 
% or a partner or director, of the main practice;

according_to(r34_2_a,may(LP,accept,EA)) :-
    legal_practitioner(LP),
    member_of(LP,Main_Practice),
    law_practice_in_singapore(Main_Practice),
    executive_appointment_in_a_law_practice(EA,Other_Practice),
    law_practice_in_singapore(Other_Practice),
    Main_Practice \= Other_Practice,
    not owner_and_not_partner_of(Other_Practice,Main_Practice).

opposes(r34_1_b,must_not(LP,accept,EA),r34_2_a,may(LP,accept,EA)).
opposes(r34_1,must_not(LP,accept,EA),r34_2_a,may(LP,accept,EA)).

overrides(r34_1_b,must_not(LP,accept,EA),r34_2_a,may(LP,accept,EA)).
overrides(r34_1,must_not(LP,accept,EA),r34_2_a,may(LP,accept,EA)).

owner_of(X,Y) :-
    legal_owner_of(X,Y).
owner_of(X,Y) :-
    beneficial_owner_of(X,Y).

partner_sp_or_director_of(X,Y) :-
    partner_of(X,Y).
partner_sp_or_director_of(X,Y) :-
    sole_proprietor_of(X,Y).
partner_sp_or_director_of(X,Y) :-
    director_of(X,Y).

owner_and_not_partner_of(Y,Z) :-
    owner_of(X,Y),
    not partner_sp_or_director_of(X,Z).


% RULE 34(2)(b)
% (b)	the legal practitioner accepts the executive appointment as a representative 
% of the main practice in the related practice, and the involvement of the main practice 
% in the related practice is not prohibited by any of the following:
% (i)	the Act;
% (ii)	these Rules or any other subsidiary legislation made under the Act;
% (iii)	any practice directions, guidance notes and rulings issued under section 71(6) of the Act;
% (iv)	any practice directions, guidance notes and rulings (relating to professional practice,
% etiquette, conduct and discipline) issued by the Council or the Society.

according_to(r34_2_b,may(LP,accept,EA)) :-
    legal_practitioner(LP),
    member_of(LP,Main_Practice), %test comment to break things
    law_practice_in_singapore(Main_Practice),
    executive_appointment_in_a_law_practice(EA,Other_Practice),
    law_practice_in_singapore(Other_Practice),
    Main_Practice \= Other_Practice,
    accepts_position_as_representative(LP,EA,Main_Practice),
    not participation_prohibited(Main_Practice,Other_Practice). % this is a low-fidelity representation of the prohibition.

opposes(r34_1,must_not(LP,accept,EA),r34_2_b,may(LP,accept,EA)).
opposes(r34_1_b,must_not(LP,accept,EA),r34_2_b,may(LP,accept,EA)).

overrides(r34_1,must_not(LP,accept,EA),r34_2_b,may(LP,accept,EA)).
overrides(r34_1_b,must_not(LP,accept,EA),r34_2_b,may(LP,accept,EA)).

% RULE 34(3)
% (3)  Subject to paragraph (1), a legal practitioner may accept an executive appointment 
% in a business entity which provides law-related services.

according_to(r34_3,may(LP,accept,EA)) :-
    legal_practitioner(LP),
    executive_appointment_in_a_business_entity(EA,BE),
    provides(BE,LRS),
    law_related_service(LRS).

opposes(r34_1,must_not(LP,accept,EA),r34_3,may(LP,accept,EA)).
opposes(r34_1_b,must_not(LP,accept,EA),r34_3,may(LP,accept,EA)).

overrides(r34_1,must_not(LP,accept,EA),r34_3,may(LP,accept,EA)).
overrides(r34_1_b,must_not(LP,accept,EA),r34_3,may(LP,accept,EA)).

% RULE 34(4)
% (4)  Subject to paragraph (1), a legal practitioner (not being a locum solicitor) may 
% accept an executive appointment in a business entity which does not provide any 
% legal services or law-related services, if all of the conditions set out in the 
% Second Schedule are satisfied.

according_to(r34_4,may(LP,accept,EA)) :-
    legal_practitioner(LP),
    not locum_solicitor(LP),
    executive_appointment_in_a_business_entity(EA,BE),
    not provides_legal_or_law_related_services(BE),
    conditions_of_second_schedule_satisfied.

opposes(r34_1,must_not(LP,accept,EA),r34_4,may(LP,accept,EA)).
opposes(r34_1_b,must_not(LP,accept,EA),r34_4,may(LP,accept,EA)).

overrides(r34_1,must_not(LP,accept,EA),r34_4,may(LP,accept,EA)).
overrides(r34_1_b,must_not(LP,accept,EA),r34_4,may(LP,accept,EA)).

% RULE 34(5)
% (5)  Despite paragraph (1)(b), but subject to paragraph (1)(a) and (c) to (f), 
% a locum solicitor may accept an executive appointment in a business entity which 
% does not provide any legal services or law-related services, if all of the 
% conditions set out in the Second Schedule are satisfied.

according_to(r34_5,may(LP,accept,EA)) :-
    legal_practitioner(LP),
    locum_solicitor(LP),
    executive_appointment_in_a_business_entity(EA,BE),
    not provides_legal_or_law_related_services(BE),
    conditions_of_second_schedule_satisfied.

opposes(r34_1,must_not(LP,accept,EA),r34_5,may(LP,accept,EA)).
opposes(r34_5,may(LP,accept,EA),r34_1_b,must_not(LP,accept,EA)).

overrides(r34_1,must_not(LP,accept,EA),r34_5,may(LP,accept,EA)).
overrides(r34_5,may(LP,accept,EA),r34_1_b,must_not(LP,accept,EA)).

provides_legal_or_law_related_services(BE) :-
    provides(BE,Serv),
    legal_service(Serv).

provides_legal_or_law_related_services(BE) :-
    provides(BE,Serv),
    law_related_service(Serv).

% RULE 34(6)
% (6)  Except as provided in paragraphs (2) to (5) —
% (a)	a legal practitioner in a Singapore law practice must not accept any executive 
% appointment in another Singapore law practice; and

according_to(r34_6_a,must_not(LP,accept,EA)) :-
    legal_practitioner(LP),
    executive_appointment_in_a_law_practice(EA,Other_Practice),
    member_of(LP,Own_Practice),
    law_practice_in_singapore(Own_Practice),
    law_practice_in_singapore(Other_Practice),
    Own_Practice \= Other_Practice.

opposes(r34_2_a,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
opposes(r34_2_b,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
opposes(r34_3,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
opposes(r34_4,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
opposes(r34_5,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).

overrides(r34_2_a,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
overrides(r34_2_b,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
overrides(r34_3,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
overrides(r34_4,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).
overrides(r34_5,may(LP,accept,EA),r34_6_a,must_not(LP,accept,EA)).

% (b)	a legal practitioner must not accept any executive appointment in a business entity.

according_to(r34_6_b,must_not(LP,accept,EA)) :-
    legal_practitioner(LP),
    executive_appointment_in_a_business_entity(EA,BE).

opposes(r34_2_a,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
opposes(r34_2_b,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
opposes(r34_3,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
opposes(r34_4,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
opposes(r34_5,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).


overrides(r34_2_a,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
overrides(r34_2_b,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
overrides(r34_3,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
overrides(r34_4,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).
overrides(r34_5,may(LP,accept,EA),r34_6_b,must_not(LP,accept,EA)).

% RULE 34(7)
% (7)  To avoid doubt, nothing in this rule prohibits a legal practitioner 
% from accepting any appointment in any institution set out in the Third Schedule.

according_to(r34_7,may(LP,accept,P)) :-
    legal_practitioner(LP),
    position(P),
    institution(I),
    in(P,I),
    in_third_schedule(I).

% DEFINITIONS
% (9)  In this rule and the First to Fourth Schedules —
% “business” includes any business, trade or calling in Singapore or elsewhere, 
% whether or not for the purpose of profit, but excludes the practice of law;

business(X) :- trade(X), X \= practice_of_law.
business(X) :- calling(X), X \= practice_of_law.
business(X) :- business(X), X \= practice_of_law. % circular much?

% “business entity”  —
% (a)	includes any company, corporation, partnership, limited liability partnership, 
% sole proprietorship, business trust or other entity that carries on any business; but
% (b)	excludes any Singapore law practice, any Joint Law Venture, any Formal Law Alliance, 
% any foreign law practice and any institution set out in the Third Schedule;

business_entity(X) :- carries_on(X,Y), business(Y), company(X), not law_practice_in_singapore(X), not joint_law_venture(X), not formal_law_alliance(X), not foreign_law_practice(X), not third_schedule_institution(X).
business_entity(X) :- carries_on(X,Y), business(Y), corporation(X), not law_practice_in_singapore(X), not joint_law_venture(X), not formal_law_alliance(X), not foreign_law_practice(X), not third_schedule_institution(X).
business_entity(X) :- carries_on(X,Y), business(Y), partnership(X), not law_practice_in_singapore(X), not joint_law_venture(X), not formal_law_alliance(X), not foreign_law_practice(X), not third_schedule_institution(X).
business_entity(X) :- carries_on(X,Y), business(Y), llp(X), not law_practice_in_singapore(X), not joint_law_venture(X), not formal_law_alliance(X), not foreign_law_practice(X), not third_schedule_institution(X).
business_entity(X) :- carries_on(X,Y), business(Y), soleprop(X), not law_practice_in_singapore(X), not joint_law_venture(X), not formal_law_alliance(X), not foreign_law_practice(X), not third_schedule_institution(X).
business_entity(X) :- carries_on(X,Y), business(Y), business_trust(X), not law_practice_in_singapore(X), not joint_law_venture(X), not formal_law_alliance(X), not foreign_law_practice(X), not third_schedule_institution(X).
business_entity(X) :- carries_on(X,Y), business(Y), not law_practice_in_singapore(X), not joint_law_venture(X), not formal_law_alliance(X), not foreign_law_practice(X), not third_schedule_institution(X).

law_practice_in_singapore(X) :-
    law_practice(X),
    jurisdiction(X,singapore).

% “executive appointment” means a position associated with a business, or in a business 
% entity or Singapore law practice, which entitles the holder of the position to perform 
% executive functions in relation to the business, business entity or Singapore law practice 
% (as the case may be), but excludes any non‑executive director or independent director 
% associated with the business or in the business entity;

executive_appointment(X) :- executive_appointment_associated_with_a_business(X,Y).
executive_appointment(X) :- executive_appointment_in_a_business_entity(X,Y).
executive_appointment(X) :- executive_appointment_in_a_law_practice(X,Y).

executive_appointment_associated_with_a_business(X,Y) :- position(X), entitles_holder(X), associated_with(X,Y), business(Y), not non_executive_director(X), not independent_director(X).
executive_appointment_in_a_business_entity(X,Y) :- position(X), entitles_holder(X), in(X,Y), business_entity(Y), not non_executive_director(X), not independent_director(X).
executive_appointment_in_a_law_practice(X,Y) :- position(X), entitles_holder(X), in(X,Y), law_practice(Y), jurisdiction(Y,singapore), not non_executive_director(X), not independent_director(X).