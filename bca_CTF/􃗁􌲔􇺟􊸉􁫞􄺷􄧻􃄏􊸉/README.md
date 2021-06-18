This was a very fun challenge as it was a classical sustitution cipher with a twist such as the plain text is a little harder to read.
Reading the file we see a bunch of unicode characters that has a high ord value. 
Using the command 
```bash 
cat ciphertext.md  | sed -e "s/.\{1\}/&\n/g" | sort | uniq 
```
We can get all the different characters in the string. The first thing that jumped out to me was how their were only 20ish characters that were unprintable.
This means that each character in the plaintext must be mapped to a simualr unicode character. In order to solve this challenge we need to first convert all the unicode characters into letter of the alphabet. The order of this does not matter as long as each mapping is uniquq we can use a website such as https://www.quipqiup.com/ to run frequency analysis on the text.
After writing some bad code we get the output of 
``
"kqpqe rikkf rhpq oiu ud" hc lmq nqjul chkrsq eqgienqn jo qkrshcm chkrqe fkn cikrwehlqe ehgx fclsqo, eqsqfcqn ik 27 buso 1987. hl wfc wehllqk fkn deinugqn jo cligx fhlxqk wflqetfk, fkn wfc eqsqfcqn fc lmq vhecl chkrsq veit fclsqo'c nqjul fsjut, wmqkqpqe oiu kqqn citqjino (1987). lmq cikr wfc f wiesnwhnq kutjqe-ikq mhl, hkhlhfsso hk lmq ukhlqn xhkrnit hk 1987, wmqeq hl clfoqn fl lmq lid iv lmq gmfel vie vhpq wqqxc fkn wfc lmq jqcl-cqsshkr chkrsq iv lmfl oqfe. hl qpqklufsso liddqn lmq gmfelc hk 25 giuklehqc, hkgsunhkr lmq ukhlqn clflqc fkn wqcl rqetfko.[6] lmq cikr wik jqcl jehlhcm chkrsq fl lmq 1988 jehl fwfenc.aalmq tuchg phnqi vie lmq cikr mfc jqgitq lmq jfchc vie lmq "ehgxeisshkr" hklqekql tqtq. hk 2008, fclsqo wik lmq tlp queidq tuchg fwfen vie jqcl fgl qpqe whlm lmq cikr, fc f eqcusl iv gissqglhpq pilhkr veit lmiucfknc iv dqidsq ik lmq hklqekql, nuq li lmq didusfe dmqkitqkik iv ehgxeisshkr.[7] lmq cikr hc gikchnqeqn fclsqo'c chrkflueq cikr fkn hl hc ivlqk dsfoqn fl lmq qkn iv mhc shpq gikgqelc.aahk 2019, fclsqo eqgienqn fkn eqsqfcqn f 'dhfkivielq' pqechik iv lmq cikr vie mhc fsjut lmq jqcl iv tq, wmhgm vqflueqc f kqw dhfki feefkrqtqkl.[8]aacmftqsqccso gidhqn veit [whxhdqnhf'c felhgsq ik lmq cujbqgl](mlldc://qk.whxhdqnhf.ier/whxh/kqpqe_rikkf_rhpq_oiu_ud)aajgfglv{cieeo_wq_efk_iul_iv_eukqc_cbemwjr}
``
Sticking this in quipquip we see the flag and a rickroll
![image](https://user-images.githubusercontent.com/77011982/122486485-27d9b800-cfa7-11eb-84eb-a5dfa8858ea0.png)
