# sCASP encoding of rps
# Reference: Jason's article at https://medium.com/computational-law-diary/how-rules-as-code-makes-laws-better-115ab62ab6c4

#pred player(X) :: '@(X) is a player'.
#pred player_in_game(Player,Game) :: '@(Player) participated in @(Game)'.
#pred winner_of_game(Player,Game) :: '@(Player) is the winner of @(Game)'.
#pred player_threw_sign(Player,Sign) :: '@(Player) threw @(Sign)'.
#pred sign_beats_sign(Sign,OtherSign) :: '@(Sign) beats @(OtherSign)'.

#beats(rock,scissors).
#beats(scissors,paper).
#beats(paper,rock).

winner(Game,Player) :-
  player(Player),
  player(OtherPlayer),
  participate_in(Game,Player),
  throw(Player,Sign),
  participate_in(Game,OtherPlayer),
  throw(OtherPlayer,OtherSign),
  beat(Sign,OtherSign),
  Player \= OtherPlayer.

