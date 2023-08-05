"""

The web url matching regex used by markdown
http://daringfireball.net/2010/07/improved_regex_for_matching_urls
https://gist.github.com/gruber/8891611

Copyright (c) 2020-2022 Ayoub Malek and Vanessa Sochat

This source code is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""

domain_extensions = "".join(
    (
        "com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|",
        "jobs|mobi|museum|name|post|pro|tel|travel|xxx|",
        "ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|",
        "ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|",
        "ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|",
        "dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|",
        "fi|fj|fk|fm|fo|fr|",
        "ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|",
        "hk|hm|hn|hr|ht|hu|",
        "id|ie|il|im|in|io|iq|ir|is|it|",
        "je|jm|jo|jp|ke|kg|kh|ki|",
        "km|kn|kp|kr|kw|ky|kz|",
        "la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|",
        "ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|",
        "na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|",
        "om|",
        "pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|",
        "qa|",
        "re|ro|rs|ru|rw|",
        "sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|",
        "tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|",
        "ua|ug|uk|us|uy|uz|",
        "va|vc|ve|vg|vi|vn|vu|",
        "wf|ws|",
        "ye|yt|yu|",
        "za|zm|zw",
    )
)

URL_REGEX = "".join(
    (
        "(?i)\\b(",
        "(?:",
        "https?:(?:/{1,3}|[a-z0-9%]",
        ")",
        "|[a-z0-9.\\-]+[.](?:%s)/)" % domain_extensions,
        "(?:",
        "[^\\s()<>\[\\]]+|\\([^\\s()]*?\\([^\\s()]+\\)[^\\s()]*?\\)",
        "|\\([^\\s]+?\\)",
        ")",
        "+",
        "(?:",
        "\\([^\\s()]*?\\([^\\s()]+\\)[^\\s()]*?\\)",
        "|\\([^\\s]+?\\)",
        "|[^\\s`!()\\[\\];:'\".,<>?«»“”‘’]",
        ")",
        "|",
        "(?:",
        "(?<!@)[a-z0-9]",
        "+(?:[.\\-][a-z0-9]+)*[.]",
        "(?:%s)\\b/?(?!@)" % domain_extensions,
        "))",
    )
)


FINAL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
