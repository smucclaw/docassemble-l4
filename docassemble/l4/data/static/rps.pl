% sCASP encoding of rps
% Reference: Jason's article at https://medium.com/computational-law-diary/how-rules-as-code-makes-laws-better-115ab62ab6c4

#pred player(X) :: '@(X) is a player'.
#pred participate_in(Game,Player) :: '@(Player) participated in @(Game)'.
#pred winner(Game,Player) :: '@(Player) is the winner of @(Game)'.
#pred throw(Player,Sign) :: '@(Player) threw @(Sign)'.
#pred beat(Sign,OtherSign) :: '@(Sign) beats @(OtherSign)'.

% the rock, paper, scissors atoms are encoded directly, and so we append "daSCASP_" as required in docassemble-scasp
beat(daSCASP_rock,daSCASP_scissors).
beat(daSCASP_scissors,daSCASP_paper).
beat(daSCASP_paper,daSCASP_rock).

winner(Game,Player) :-
  game(Game),
  player(Player),
  player(OtherPlayer),
  participate_in(Game,Player),
  throw(Player,Sign),
  participate_in(Game,OtherPlayer),
  throw(OtherPlayer,OtherSign),
  beat(Sign,OtherSign),
  Player \= OtherPlayer.

