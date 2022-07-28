
nuImages内の画像をプレビューするツールを作りました．
対象オブジェクトの2D-BBox高さ，マスクエリア，元画像と，2D-BBoxを描画した画像を表示します．
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1706665/14ae369b-408e-8158-7d73-b451be7cd796.png)

# 環境
- Mac mini (M1, 2020. Monterey 12.3.1)
- Python 3.8.5(conda 4.12.0)
- Tkinter 8.6


# 前準備
(そのうち記事にするかも？)  
nuImagesのチュートリアル，Data Schemaを参考に，以下の情報が含まれるファイルを用意します．
- 対象オブジェクト(歩行者)のtoken 
- 対象オブジェクトのBBoxサイズとマスクエリアサイズ
- 対象オブジェクトが映る画像(\<ori img\>と定義)のパス
- 対象オブジェクトに2D-BBoxを描画した画像(\<ann img\>と定義)とそのパス

今回はndjson形式で収集しました．csvなどでもいいと思います．

```ndjson:ped.ndjson(例)
{"token": "014c6d598b6341659049734b16bc8034", "bbox_size": [987, 415, 1037, 501], "mask_size": [900, 1600], "mask_area": 639, "ori_img": "samples/CAM_BACK_LEFT/n015-2018-09-19-11-19-35+0800__CAM_BACK_LEFT__1537327456197423.jpg", "new_img": "./im_ped/v1.0-mini/n015-2018-09-19-11-19-35+0800__CAM_BACK_LEFT__1537327456197423/014c6d598b6341659049734b16bc8034.jpg"}
{"token": "01c21ffe79704c4fa6eb7864d6e111ee", "bbox_size": [360, 415, 397, 493], "mask_size": [900, 1600], "mask_area": 371, "ori_img": "samples/CAM_BACK_LEFT/n015-2018-09-19-11-19-35+0800__CAM_BACK_LEFT__1537327456197423.jpg", "new_img": "./im_ped/v1.0-mini/n015-2018-09-19-11-19-35+0800__CAM_BACK_LEFT__1537327456197423/01c21ffe79704c4fa6eb7864d6e111ee.jpg"}
{"token": "061292a56b6f4901851023e000581926", "bbox_size": [94, 421, 118, 471], "mask_size": [900, 1600], "mask_area": 350, "ori_img": "samples/CAM_BACK_LEFT/n015-2018-09-19-11-19-35+0800__CAM_BACK_LEFT__1537327456197423.jpg", "new_img": "./im_ped/v1.0-mini/n015-2018-09-19-11-19-35+0800__CAM_BACK_LEFT__1537327456197423/061292a56b6f4901851023e000581926.jpg"}
```

あとは設計図が重要です．途中作りながら仕様を変えたので，多少相違はありますが，こんな感じを目標にしていました．
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1706665/77ab0ab3-73fe-92fd-c57f-fb6282545da7.png)
(画像ファイルパスの入力をやめて，オブジェクトtokenにしました)

# 解説
```python
j_file = '/hoge/piyo/ped.ndjson'
ann_datas = {}
ori_img_root = '/hoge/foo/'
ann_img_root = '/hoge/fuga/'
```
"準備"節で紹介した各ファイルの参照です．
- `j_file`にped.ndjsonを指定します．
- `ori_img_root`はped.ndjsonで指定したパスを補完します．後で，`ori_img_root + {ped.ndjson内の画像パス}`で画像を参照します．
- `ann_img_root`も同様です．

```python:Applicationの__init__
self.img_width = 550
self.img_height = int(self.img_width/1.79)
```
nuImagesの画像サイズに合わせています．width側を変えれば，高さも正しくなるはず...

`create_widget`内は各領域を定義しています．ほぼ先行記事を参考に作りました．(説明略)

```python:loadInstance
self.ann_token = self.ann_token_box.get()

try:
    self.ori_img_filepath = ann_datas[self.ann_token]['ori_img']
    self.ori_img_filepath = ori_img_root + self.ori_img_filepath
    print("ori : ", self.ori_img_filepath)

    self.ann_img_filepath = ann_datas[self.ann_token]['ann_img']
    self.ann_img_filepath = ann_img_root + self.ann_img_filepath[2:]
    self.ann_maskarea = ann_datas[self.ann_token]['mask_area']
    self.ann_bboxheight = ann_datas[self.ann_token]['bbox_height']
    print("ann : ", self.ann_img_filepath)
except KeyError:
    print(f"The token ({self.ann_token}) is not defined.")
except Exception as e:
    print(self.ann_token, e)
```
テキストボックスに記入されたtokenを取得して，それをkeyに辞書(ann_datas)から必要な情報を取得します．
最近ようやくtry...except節を使うようになりました．
大きなデータを扱うときや操作次第でエラーが出ることがわかっていれば，事前に定義しておけばプログラムが止まらなくて便利です．
`KeyError`はndjson内にないtokenを指定した場合や，空欄のまま実行した場合に発火します．
`Exception`はその他，すべてのエラーを拾ってくれます．ワイルドカードの`except`でもすべてのエラーを拾ってくれますが，`KeyboardInterrupt`はじめ終了処理も受け取ってしまい，終了が難しくなります．
> すべての例外をキャッチするので、SystemExit（sys.exit()などが送出）、KeyboardInterrupt（割り込みキーCtrl + C入力で送出）もキャッチしてしまう
> [Pythonの例外処理（try, except, else, finally） | note.nkmk.me](https://note.nkmk.me/python-try-except-else-finally/)

```python:loadInstance
# Update info
self.info_canvas.delete("maskarea")
self.info_canvas.delete("bboxheight")
self.info_canvas.create_text(10, 30, text=f"Mask area\t: {self.ann_maskarea}", font=("Ricty", 24), anchor="nw", tag="maskarea")  # 左上原点
self.info_canvas.create_text(10, 60, text=f"BBox height\t: {self.ann_bboxheight}", font=("Ricty", 24), anchor="nw", tag="bboxheight")  # 左上原点
```
右上のマスク面積，BBox高さについて，{既に書いてある内容の削除}->{読み込んだ画像の情報を記録}という手順をとっています．

```python:loadInstance
# ori_img
self.ori_img_bgr = cv2.imread(self.ori_img_filepath)
self.ori_img_height, self.ori_img_width = self.ori_img_bgr.shape[:2]
self.ori_img_bgr_resize = cv2.resize(self.ori_img_bgr, (self.img_width, self.img_height), interpolation=cv2.INTER_AREA)
self.ori_img_rgb = cv2.cvtColor( self.ori_img_bgr_resize, cv2.COLOR_BGR2RGB )  # imreadはBGRなのでRGBに変換
self.ori_img_PIL = Image.fromarray(self.ori_img_rgb) # RGBからPILフォーマットへ変換
self.ori_img_tk = ImageTk.PhotoImage(self.ori_img_PIL) # ImageTkフォーマットへ変換
self.ori_img_canvas.create_image(self.img_width/2, self.img_height/2, image=self.ori_img_tk)
```
指定した画像を読み込み，tkinterでの表示に適した形式に変換します．先行記事を参考にしたので，説明は省略します．  

今回で一番クソコードの自覚がある場所です．  
本当は関数にして，ann_imgとうまく共有したかったのですが，Imageのインスタンスを上書きしてしまい，後から出力するann_imgしか出力されない課題にぶち当たり，愚直な方法で解決しました．  
なにか良い解決策がある方，ご教示いただけると嬉しいです．　　
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1706665/e5af2737-357e-6d3e-c9ee-81418041e065.png)　　
> Image のインスタンスを保持している変数(img) がループで上書きされたことにより、ガベージコレクションが何処からも参照されていないImage のインスタンスを削除してしまう事が原因でしょう。
> Imageのインスタンスをリスト等で保持することで解決するかと思います。
> [Tkinter 複数の画像の表示](https://teratail.com/questions/202187)

```python:oriSave
def oriSave(self):
    savePath = tk.filedialog.asksaveasfilename(
        initialfile=self.ann_token + "_ori", 
        defaultextension="jpg"
    )
    # self.ori_img_PIL.save(savePath + ".jpg")  # 縮小後の画像が保存される
    try:
        shutil.copy2(self.ori_img_filepath, savePath)
    except PermissionError as e:
        print(f"Permission Error\n保存に失敗した可能性があります．\n{savePath}.jpgを確認してください\n{e}")
    except FileNotFoundError:
        print("Canceled")
    except Exception as e:
        print(f"Undefined Error : {e}\n{self.ori_img_filepath} -> {savePath}")
```
設計にはなかった部分です．
表示された画像を使いたい！と思った時，元ファイルへの参照が面倒なので，ボタン一発で任意のディレクトリにコピーできるようにしました．

ここでもtry...except節を活用しています．  
私の環境ではデスクトップに保存した際，なぜか`PermissionError`が発火します．実行環境がデスクトップへのファイルアクセスを許可されていないためでしょうか？エラーは出ますが，ファイルの保存には成功しているので目を瞑りました．  
`FileNotFoundError`はファイルダイアログでキャンセルした場合に発火します．今回はファイルダイアログで指定するので，そのようなケースはないはずですが，存在しないディレクトリを参照した場合も発火すると思います．  
`Exception`節はその他，予期していないエラーの出力です．今の所出くわしていません．

`annSave`もほぼ同じです．  
ori_imgとann_imgでうまく関数を共有したかったのですが，私のコーディングスキル不足で別関数になりました．
このプレビューツールは作業の効率化のためで，メインの作業ではなかったので，愚直な方法に妥協しました．動くことFIRSTです．

`read_json`はped.ndjsonに合わせています．ndjsonはほぼjsonのような形式で，改行でレコードを記録するようです．  
nuImagesはデータ数が非常に多く，走査時にすべてを変数に保持して，最後にjsonファイルを記録するような行為が難しいと判断しました．そこで，歩行者を見つけるごとにその情報をファイルに追記することにし，その際に改行で記録できるndjsonが勝手が良く，採用しました．ファイルへのアクセス回数が増えるのは欠点かもしれません．  
最近ではコロナ関連のオープンデータにも多く使われているようです．  

# まとめ
事前に情報を取得したオブジェクトに対し，nuImagesの画像をプレビューするツールを作成しました．  
歩行者だけ，車だけ，...を先に抜粋し，それらの大きさなどを順に確認したいときに役立つと思います．
メインのプログラムでないことを言い訳に，愚直なコードで解決した部分があるので，今後の反省点としてとどめておこうと思います．


# 参考記事
[TkinterでImage Viewerを制作 - Qiita](https://qiita.com/kotai2003/items/7f23dc604a6b4b3b5898)
