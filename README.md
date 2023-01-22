## 簡単な説明でわかる方
こちら私の記事です 一通りやり方書いてます

>https://qiita.com/chihiro-yabuta/items/72e4a1869e9196ca9a67

## 詳細な説明が必要な方（上田研の方

### Step1: docker をインストールしましょう
ここからdockerをインストールします

>https://docs.docker.com/desktop/mac/apple-silicon/

こちらM1 Macbook Air用なので各々調べて下さい

![version](git/version.png)

インストールできたらアプリを立ち上げておきましょう<br>
docker desktopを立ち上げないとdockerは動かせません

### Step2: vscode に拡張機能をインストールしましょう
この二つインストールして下さい<br>
vscodeは調べてインストールして下さい

![docker](git/extension_docker.png)
![containers](git/extension_containers.png)

### Step3: clone しましょう
リポジトリをclone (zip downloadでも構いません) しましょう<br>
gitは既にmacに入っていると思うのでターミナルを立ち上げて

```
git clone https://github.com/chihiro-yabuta/elegant-curve.git
```

を叩きましょう

### Step4: コンテナを立ち上げましょう
cloneしたディレクトリを開いて

```
make
```

を叩きましょう

![build](git/build.png)

また、以下のようなディレクトリが出来ているのでinputに実行したいcsvを入れましょう

<pre>
.
├── archive
│   ├── * (計算過程のデータが格納されます)
├── input
│   ├── *.csv (実行されるファイルです)
├── output
│   ├── *.csv (結果がここに出力されます)
</pre>

立ち上がったらcontainerにattachしましょう

![attach](git/attach.png)

attachできたら

```
python main.py
```

で走らせましょう

![run](git/run.png)

お疲れ様でした
