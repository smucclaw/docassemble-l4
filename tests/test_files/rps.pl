% sCASP encoding of rps
% Reference: Jason's article at https://medium.com/computational-law-diary/how-rules-as-code-makes-laws-better-115ab62ab6c4

#pred player(X) :: '@(X) is a player'.
#pred participate_in(Game,Player) :: '@(Player) participated in @(Game)'.
#pred winner(Game,Player) :: '@(Player) is the winner of @(Game)'.
#pred throw(Player,Sign) :: '@(Player) threw @(Sign)'.
#pred beat(Sign,OtherSign) :: '@(Sign) beats @(OtherSign)'.

beats(rock,scissors).
beats(scissors,paper).
beats(paper,rock).

winner(Game,Player) :-
  player(Player),
  player(OtherPlayer),
  participate_in(Game,Player),
  throw(Player,Sign),
  participate_in(Game,OtherPlayer),
  throw(OtherPlayer,OtherSign),
  beat(Sign,OtherSign),
  Player \= OtherPlayer.