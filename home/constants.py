language_choices = (
    ("en", "English"),
    ("hi", "Hindi"),
    ("te", "Telugu"),
    ("ta", "Tamil"),
    ("ml", "Malayalam"),
    ("kn", "Kannada"),
    ("od", "Odia"),
    ("bn", "Bengali"),
    ("gu", "Gujarati"),
    ("mr", "Marathi"),
    ("pa", "Punjabi"),
    ("ur", "Urdu"),
    ("otr", "Other"),
)

category_choices = (
    ("report", "Report"),
    ("case_study", "Case Study"),
    ("interview", "Interview"),
    ("journal_article", "Journal Article"),
    ("journal_edition", "Journal Edition"),
    ("study", "Study"),
    ("manual", "Manual"),
    ("directory", "Directory"),
    ("other", "Other"),
)

file_types = (
    ("pdf", "PDF"),
    ("doc", "DOC"),
    ("ppt", "PPT"),
    ("txt", "TXT"),
    ("img", "IMG"),
)

url_types = (
    ("youtube", "Youtube"),
)

state_choices = (
    ("ad", "Andhra Pradesh"),
    ("ar", "Arunachal Pradesh"),
    ("as", "Assam"),
    ("br", "Bihar"),
    ("cg", "Chattisgarh"),
    ("dl", "Delhi"),
    ("ga", "Goa"),
    ("gj", "Gujarat"),
    ("hr", "Haryana"),
    ("hp", "Himachal Pradesh"),
    ("jk", "Jammu and Kashmir"),
    ("jh", "Jharkhand"),
    ("ka", "Karnataka"),
    ("kl", "Kerala"),
    ("ld", "Lakshadweep Islands"),
    ("mp", "Madhya Pradesh"),
    ("mh", "Maharashtra"),
    ("mn", "Manipur"),
    ("ml", "Meghalaya"),
    ("mz", "Mizoram"),
    ("nl", "Nagaland"),
    ("od", "Odisha"),
    ("py", "Pondicherry"),
    ("pb", "Punjab"),
    ("rj", "Rajasthan"),
    ("sk", "Sikkim"),
    ("tn", "Tamil Nadu"),
    ("ts", "Telangana"),
    ("tr", "Tripura"),
    ("up", "Uttar Pradesh"),
    ("uk", "Uttarakhand"),
    ("wb", "West Bengal"),
    ("an", "Andaman and Nicobar Islands"),
    ("ch", "Chandigarh"),
    ("dnhdd", "Dadra & Nagar Haveli and Daman & Diu"),
    ("la", "Ladakh"),
)

status_choices = (
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("processed", "Processed"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("error", "Error")
)


def get_display_name(input_list, key):
    for item in input_list:
        if item[0] == key:
            return item[1]
    return None
