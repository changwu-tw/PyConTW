# SageMath


## 1. 安裝 SageMath

一套整合了 Numpy, Scipy, Matplotlib, R .. 等科學計算的數學開源軟體

- 下載 [http://www.sagemath.org/download-mac.html](http://www.sagemath.org/download-mac.html)
- 按指示安裝: http://files.sagemath.org/osx/README.txt

電子書: [http://dl.lateralis.org/public/sagebook/sagebook-ba6596d.pdf](http://dl.lateralis.org/public/sagebook/sagebook-ba6596d.pdf)


## 2. 安裝後

在 terminal 鍵入 sage 就可開始使用 (如見下圖，表示安裝完成)

![](https://cl.ly/6bfaeadb4204/Image%2525202019-11-20%252520at%25252012.48.22%252520PM.png)

始終在命令列執行還是不方便，雖然他有 Sage Notebook 的版本，但還是想用 Jupyter Notebook


## 3. 安裝 Jupyter

Jupyter ([http://jupyter.org/](http://jupyter.org/)) 是一套互動式的引擎，支援程式計算，環境如下

```bash
$ python -V
Python 2.7.15

$ pip install jupyter
$ sage -n jupyter
```

## 4. 啟動 SageMath on Jupyter

![](https://cl.ly/965be22fe00a/Image%2525202019-11-20%252520at%25252012.50.40%252520PM.png)

開啟連結

## 5. 開啟 Jupyter

由於 Jupyter 會根據你要執行的計算引擎，所以這邊會選 SageMath 8.3

![](https://cl.ly/fe37fc7081bc/Image%2525202019-11-20%252520at%25252012.51.33%252520PM.png)

## 6. 新增 notebook 後，執行看看

```python
# https://github.com/TheBlueMatt/bitcoinninja/blob/master/secp256k1.ecdsa.sage
# Parameters for secp256k1
# https://en.bitcoin.it/wiki/Secp256k1
F = FiniteField(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
C = EllipticCurve([F(0), F(7)])                                # y^2=x^3+ax+b
G = C.lift_x(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
N = FiniteField(C.order())                                     # how many points on the curve

# primitive
d = int(F.random_element())                                    # privkey
# d = int(82239264722932775278839278822102466293134098816780207494037340746696852842337)
pd = G*d                                                       # pubkey
e = int(''.join(i.encode('hex') for i in 'hello'), 16)         # message('hello')

# sign
k = N.random_element()                                         # nonce
r = (int(k)*G).xy()[0]                                         # r = kG.x
s = (1/k)*(e+N(r)*d)                                           # s = k^-1(e+dr)

# verify
w = 1/N(s)                                                     # w = s^-1
r == (int(w*e)*G + int(N(r)*w)*pd).xy()[0]                     # r == (we*G+wr*pd).x

```
