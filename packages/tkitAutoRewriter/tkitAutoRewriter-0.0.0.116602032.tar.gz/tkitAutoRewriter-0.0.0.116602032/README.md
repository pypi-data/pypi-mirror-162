# 自动重写内容SDK 英文版本

主要是调用的封装

实现自动重写内容，英文版本

##安装

> pip install tkitAutoRewriter


## 示例
自动对内容筛选

```python
from tkitAutoRewriter.api import SentenceClassification

cls=SentenceClassification(api="http://192.168.1.18:3007")

text_list="""

Leading pet insurance options examined
We’ve been around for a long time and have had the good fortune of working with some of the best and worst insurance companies around. Now that we know which ones are worthy of your attention—and your hard-earned money—we’re able to bring you our comprehensive list of the ones that are at the top of our recommended pile.

Trupanion Medical Insurance for the Life of Your Pet
trupanion insuranceOur Canadian readers might be well aware of this company since they’re one of the most popular pet insurance providers in the country, but we’re here to now spread the name of Trupanion to everyone else.

Their coverage is about as good as any other provider by covering everything from accidents to congenital illnesses, and their rates are quite fair. The real selling point, however, is the unparalleled flexibility that they offer to customers who have variable needs.

Unlike most pet insurance companies that have harsh penalties and restrictions on changing your coverage, Trupanion allows their users to adjust their monthly payments on a month-to-month basis. That means people with seasonal or unstable income can continue to stay covered, which is quite appreciated by consumers.

On top of this, rates won’t change as your pet ages. These two factors combined mean that Trupanion is one of the best long-term insurance providers since you never have to worry about being locked into a plan that can suddenly become too expensive.

The process of getting paid has never been more straightforward, either. There’s no paperwork, no filing, and no lengthy phone calls to different customer service representatives who are giving you different answers.

Thanks to the fact that Trupanion is recognized by veterinarians around North America, once you’re covered, you simply have to pay your bill at the checkout counter of your local veterinarian, and they’ll send out your insurance request right then and there.


"""

out=cls.predict_text_pet(text_list=text_list)
print(out)
# {'results': [[{'label': 'yes', 'score': 0.9999681711196899}]]}




```

内容重写示例

````python
from tkitAutoRewriter import AutoReWrite, SentenceClassification

text = """

The Border Collie is a British breed of herding dog of medium size. They are descended from landrace sheepdogs once found all over the British Isles, but became standardized in the Anglo-Scottish border region. Presently they are used primarily as working dogs to herd livestock, specifically sheep.[1]

The Border Collie is considered a highly intelligent, extremely energetic, acrobatic and athletic dog. They frequently compete with great success in sheepdog trials and a range of dog sports like dog obedience, disc dog, herding and dog agility. They are one of the most intelligent domestic dog breeds.[2] Border Collies continue to be employed in their traditional work of herding livestock throughout the world and are kept as pets.

"""
rewriter = AutoReWrite(api='http://192.168.1.18:3008')
out = rewriter.rewriter(text, simlimit=0.7)
print("".join(out))
# The Border Collie is a medium-sized herding dog.They are descended from landrace sheepdogs that were once found all over the British Isles, but became standardized in the Anglo-Scottish border region.They are mostly used as working dogs to herd sheep.Presently they are used primarily as working dogs to herd livestock, specifically sheep.[1]The Border Collie is a dog that is very athletic and energetic.They compete in a variety of dog sports, including sheepdog trials and dog agility.Border Collies are one of the most intelligent domestic dog breeds, and are kept as pets.

````






容器镜像托管
>内容判别
https://gitlab.com/napoler/SequenceClassification/container_registry

> 英文生成相关
https://gitlab.com/napoler/tkittextensummary/container_registry


更多内容 
博客 https://www.terrychan.org/2022/07/%e8%8b%b1%e6%96%87%e5%86%85%e5%ae%b9%e8%87%aa%e5%8a%a8%e9%87%8d%e5%86%99sdk/

