export memory memory(initial: 1, max: 0);

data d_bjsxPKMH7ND3bPRe(offset: 1000) = 
"bjsxPKMH|"7N\1bD\043b]PR\19e%\7f/;\17";

function cmp(a, b):int {
  var $interator:
  var v0:The string of data?
  var v1:This is the user input
  loop L_a {
    if (($interator + v0)[0] != (($interator + v1)[0] ^ ($interator * 9 & 127)) & 
        $interator != 27) {
      return 0
    }
    $interator = $interator + 1;
    if (eqz(($interator - 1 + v0)[0])) { return 1 }
    continue L_a;
  }
  return 0;
}

export function checkFlag(a:int):int {
  return cmp(a, 1000)
}

