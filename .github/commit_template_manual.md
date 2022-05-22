# 커밋 메시지 템플릿 적용하기


먼저 `git clone` 으로 .gitmessage.txt를 로컬로 불러오세요.

그 후,<br>
`git config --local commit.template .github/.gitmessage.txt`<br>
명령어를 통하여 git commit template을 설정하세요.

이후에 commit을 할 때,<br>
`git commit`<br>
를 입력하면 커밋 템플릿이 뜰겁니다!

이제 명시한 위치에 커밋 메시지를 작성하세요.

커밋 메시지를 작성했다면,<br>

**✋ 리눅스 bash나 VSCode 쓰시는 경우**

`Ctrl + x`<br>
을 누르시면 저장메시지가 뜨는데, `y`를 누르면 자동으로 저장이 됩니다.

이후 Enter를 누르시면 commit 메시지 적용 완료입니다!

**✋ git bash 쓰시는 경우**

`:wq` 로 저장하시면 됩니다. 

<br>

마지막으로 `git push` 사용하시면 됩니다.
