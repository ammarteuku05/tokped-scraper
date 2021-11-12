"""
Simple script to extract the top 100 product data from tokopedia search result

Usage: simply run the script by running python tokopedia-scraper.py and enter your search keyword when prompted
"""

from bs4 import BeautifulSoup as bs
import csv
import requests


TOKOPEDIA_API_URL = 'https://gql.tokopedia.com/'


def get_search_result(search_keyword, page=1, max_retries=3):
    """
    Get the json response from tokopedia api for product search result based on the keyword and page

    Args:
        - search_keyword (str): keyword of product you want to search form
        - page (int): the page number of search result
        - max_retries (int): in case the api failed to response, how many times we should retry to call the api again

    Returns:
        - api_response (json): the api response from tokopedia search result
    """

    api_response = ''
    # Given query body and referer from tokopedia to get the search results
    query_body = [{"operationName":"SearchProductQueryV4","variables":{"params":f"device=desktop&navsource=home&ob=23&page={page}&q={search_keyword}&related=true&rows=60&safe_search=false&scheme=https&shipping=&source=search&st=product&start=0&topads_bucket=true&unique_id=14ed3345ffad7b4017c80de8e7bfda49&user_addressId=&user_cityId=176&user_districtId=2274&user_id=&user_lat=&user_long=&user_postCode=&variants="},"query":"query SearchProductQueryV4($params: String!) {\n  ace_search_product_v4(params: $params) {\n    header {\n      totalData\n      totalDataText\n      processTime\n      responseCode\n      errorMessage\n      additionalParams\n      keywordProcess\n      __typename\n    }\n    data {\n      isQuerySafe\n      ticker {\n        text\n        query\n        typeId\n        __typename\n      }\n      redirection {\n        redirectUrl\n        departmentId\n        __typename\n      }\n      related {\n        relatedKeyword\n        otherRelated {\n          keyword\n          url\n          product {\n            id\n            name\n            price\n            imageUrl\n            rating\n            countReview\n            url\n            priceStr\n            wishlist\n            shop {\n              city\n              isOfficial\n              isPowerBadge\n              __typename\n            }\n            ads {\n              adsId: id\n              productClickUrl\n              productWishlistUrl\n              shopClickUrl\n              productViewUrl\n              __typename\n            }\n            badges {\n              title\n              imageUrl\n              show\n              __typename\n            }\n            ratingAverage\n            labelGroups {\n              position\n              type\n              title\n              url\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      suggestion {\n        currentKeyword\n        suggestion\n        suggestionCount\n        instead\n        insteadCount\n        query\n        text\n        __typename\n      }\n      products {\n        id\n        name\n        ads {\n          adsId: id\n          productClickUrl\n          productWishlistUrl\n          productViewUrl\n          __typename\n        }\n        badges {\n          title\n          imageUrl\n          show\n          __typename\n        }\n        category: departmentId\n        categoryBreadcrumb\n        categoryId\n        categoryName\n        countReview\n        discountPercentage\n        gaKey\n        imageUrl\n        labelGroups {\n          position\n          title\n          type\n          url\n          __typename\n        }\n        originalPrice\n        price\n        priceRange\n        rating\n        ratingAverage\n        shop {\n          shopId: id\n          name\n          url\n          city\n          isOfficial\n          isPowerBadge\n          __typename\n        }\n        url\n        wishlist\n        sourceEngine: source_engine\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]
    referer = f'https://www.tokopedia.com/search?st=product&q={search_keyword}&navsource=home'

    # Standard header for us to be able to make an allowed and recognized api calls to tokopedia
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://www.tokopedia.com',
        'referer': f'{referer}',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    # Retry x times
    for _ in range(max_retries):
        try:
            resp = requests.post(TOKOPEDIA_API_URL, headers=headers, json=query_body)
            if resp.ok:
                api_response = resp.json()
                break
            else:
                resp.raise_for_status()
        except Exception as e:
            print(f'Tokopedia api calls failed due to: {e}')

    return api_response


def parse_search_result_data(api_response):
    """
    Parse the search result data from the given raw json by following the response style of tokopedia

    Arg:
        - api_response (list): list of products

    Returns:
        - product_list (list): list of compiled product properties
    """

    product_list = []
    for resp in api_response:
        product_results = resp.get('data').get('ace_search_product_v4').get('data').get('products') # Standard tokopedia response style
        for product in product_results:
            product_dict = dict(
                product_name=product.get('name'),
                product_image_link=product.get('imageUrl'),
                product_price=product.get('price'),
                product_rating=product.get('rating'),
                product_average_rating=product.get('ratingAverage'),
                product_merchant=product.get('shop').get('name'),
                product_target_url=product.get('url') # Going to be used to crawl further into the product page itself, to extract description
            )
            product_list.append(product_dict)

    return product_list


# TODO: figure out why backend calls for post to this url doesn't work, find the proper headers to pass
def get_product_result(product_page_url):
    """
    Get the json response from tokopedia api for product page based on the url given

    Arg:
        - product_page_url (str): url of the product page to parse

    Return:
        - api_response (json): the api response from tokopedia search result
    """

    api_response = ''
    # The given product page url always follow this pattern:
    # https://{shop_domain}/{product_key}?whid=0
    splitted_product_page_url = product_page_url.split('/')
    shop_domain = splitted_product_page_url[-2]
    product_key = splitted_product_page_url[-1].split('?')[0]
    query_body = [{"operationName":"PDPGetLayoutQuery","variables":{"shopDomain":f"{shop_domain}","productKey":f"{product_key}","layoutID":"","apiVersion":1,"userLocation":{"addressID":"0","districtID":"2274","postalCode":"","latlon":""}},"query":"fragment ProductVariant on pdpDataProductVariant {\n  errorCode\n  parentID\n  defaultChild\n  sizeChart\n  variants {\n    productVariantID\n    variantID\n    name\n    identifier\n    option {\n      picture {\n        urlOriginal: url\n        urlThumbnail: url100\n        __typename\n      }\n      productVariantOptionID\n      variantUnitValueID\n      value\n      hex\n      __typename\n    }\n    __typename\n  }\n  children {\n    productID\n    price\n    priceFmt\n    optionID\n    productName\n    productURL\n    picture {\n      urlOriginal: url\n      urlThumbnail: url100\n      __typename\n    }\n    stock {\n      stock\n      isBuyable\n      stockWordingHTML\n      minimumOrder\n      maximumOrder\n      __typename\n    }\n    isCOD\n    isWishlist\n    campaignInfo {\n      campaignID\n      campaignType\n      campaignTypeName\n      campaignIdentifier\n      background\n      discountPercentage\n      originalPrice\n      discountPrice\n      stock\n      stockSoldPercentage\n      startDate\n      endDate\n      endDateUnix\n      appLinks\n      isAppsOnly\n      isActive\n      hideGimmick\n      isCheckImei\n      __typename\n    }\n    thematicCampaign {\n      additionalInfo\n      background\n      campaignName\n      icon\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ProductMedia on pdpDataProductMedia {\n  media {\n    type\n    urlThumbnail: URLThumbnail\n    videoUrl: videoURLAndroid\n    prefix\n    suffix\n    description\n    __typename\n  }\n  videos {\n    source\n    url\n    __typename\n  }\n  __typename\n}\n\nfragment ProductHighlight on pdpDataProductContent {\n  name\n  price {\n    value\n    currency\n    __typename\n  }\n  campaign {\n    campaignID\n    campaignType\n    campaignTypeName\n    campaignIdentifier\n    background\n    percentageAmount\n    originalPrice\n    discountedPrice\n    originalStock\n    stock\n    stockSoldPercentage\n    threshold\n    startDate\n    endDate\n    endDateUnix\n    appLinks\n    isAppsOnly\n    isActive\n    hideGimmick\n    __typename\n  }\n  thematicCampaign {\n    additionalInfo\n    background\n    campaignName\n    icon\n    __typename\n  }\n  stock {\n    useStock\n    value\n    stockWording\n    __typename\n  }\n  variant {\n    isVariant\n    parentID\n    __typename\n  }\n  wholesale {\n    minQty\n    price {\n      value\n      currency\n      __typename\n    }\n    __typename\n  }\n  isCashback {\n    percentage\n    __typename\n  }\n  isTradeIn\n  isOS\n  isPowerMerchant\n  isWishlist\n  isCOD\n  isFreeOngkir {\n    isActive\n    __typename\n  }\n  preorder {\n    duration\n    timeUnit\n    isActive\n    preorderInDays\n    __typename\n  }\n  __typename\n}\n\nfragment ProductCustomInfo on pdpDataCustomInfo {\n  icon\n  title\n  isApplink\n  applink\n  separator\n  description\n  __typename\n}\n\nfragment ProductInfo on pdpDataProductInfo {\n  row\n  content {\n    title\n    subtitle\n    applink\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDetail on pdpDataProductDetail {\n  content {\n    title\n    subtitle\n    applink\n    showAtFront\n    isAnnotation\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDataInfo on pdpDataInfo {\n  icon\n  title\n  isApplink\n  applink\n  content {\n    icon\n    text\n    __typename\n  }\n  __typename\n}\n\nfragment ProductSocial on pdpDataSocialProof {\n  row\n  content {\n    icon\n    title\n    subtitle\n    applink\n    type\n    rating\n    __typename\n  }\n  __typename\n}\n\nquery PDPGetLayoutQuery($shopDomain: String, $productKey: String, $layoutID: String, $apiVersion: Float, $userLocation: pdpUserLocation!) {\n  pdpGetLayout(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, apiVersion: $apiVersion, userLocation: $userLocation) {\n    name\n    pdpSession\n    basicInfo {\n      alias\n      isQA\n      id: productID\n      shopID\n      shopName\n      minOrder\n      maxOrder\n      weight\n      weightUnit\n      condition\n      status\n      url\n      needPrescription\n      catalogID\n      isLeasing\n      isBlacklisted\n      menu {\n        id\n        name\n        url\n        __typename\n      }\n      category {\n        id\n        name\n        title\n        breadcrumbURL\n        isAdult\n        detail {\n          id\n          name\n          breadcrumbURL\n          isAdult\n          __typename\n        }\n        __typename\n      }\n      txStats {\n        transactionSuccess\n        transactionReject\n        countSold\n        paymentVerified\n        itemSoldPaymentVerified\n        __typename\n      }\n      stats {\n        countView\n        countReview\n        countTalk\n        rating\n        __typename\n      }\n      __typename\n    }\n    components {\n      name\n      type\n      position\n      data {\n        ...ProductMedia\n        ...ProductHighlight\n        ...ProductInfo\n        ...ProductDetail\n        ...ProductSocial\n        ...ProductDataInfo\n        ...ProductCustomInfo\n        ...ProductVariant\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]

    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://www.tokopedia.com',
        'content-length': '5408',
        'referer': f'{product_page_url}',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'x-tkpd-akamai': 'pdpGetLayout'
    }
    resp = requests.post(TOKOPEDIA_API_URL, headers=headers, json=query_body)
    if resp:
        api_response = resp.json()

    return api_response


# TODO: figure out why the content of the get request to the taget url doesn't work
def get_product_description(product_page_url):
    """
    Get the product description of a given product page url

    Arg:
        - product_page_url (str): product page url to go

    Returns:
        - product_description (str)
    """

    product_description = ''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    }
    # Still doens't work for now, point for improvements
    # page_content = requests.get(product_page_url, headers=headers, timeout=1).content
    page_content = ''
    if page_content:
        soup = bs(page_content, 'lxml')
        product_description = soup.find('div', {'data-testid': 'lblPDPDescriptionProduk'})

    return product_description


def write_into_csv(product_data, search_keyword):
    """
    Write the result into csv file

    Arg:
        - product_data (list of dict)
        - search_keyword (str)
    """

    data_list = []
    for product in product_data:
        data_list.append([
            product.get('product_name'),
            product.get('product_image_link'),
            product.get('product_price'),
            product.get('product_rating'),
            product.get('product_average_rating'),
            product.get('product_description'),
            product.get('product_merchant')
        ])
    file_header = ['Product Name', 'Product Image Link', 'Product Price', 'Product Rating', 'Product Average Rating', 'Product Description', 'Merchant Name']

    with open(f'Top 100 {search_keyword}.csv', 'w', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(file_header)
        writer.writerows(data_list)


def main(search_keyword):
    """
    Main script to get the data

    Arg:
        - search_keyword (str)
    """
    # Begin with search first page
    page = 1
    product_data = []
    # To get top 100 results, we check the parsed data len, if the data insufficient keep crawling to next page,
    # Default response from Tokopedia is 60 products per page
    while len(product_data) < 100:
        # To avoid infinite loop, make an assumption to do hard stop at page 5 no matter what the result
        if page >= 5:
            break
        # Get the response from tokopedia api
        search_result = get_search_result(search_keyword, max_retries=1, page=page)
        # Increase page number to crawl thru next page
        page += 1
        if search_result:
            parsed_data = parse_search_result_data(search_result)
            product_data.extend(parsed_data)

    # Only get the top 100
    if len(product_data) >= 100:
        product_data = product_data[:100]

    for product in product_data:
        try:
            product_description = get_product_description(product.get('product_target_url'))
        except Exception as e:
            print(f'Failed to get the product description due to: {e}')
            product_description = ''
        product['product_description'] = product_description

    # Write into csv file
    write_into_csv(product_data, search_keyword)

    return product_data


if __name__ == '__main__':
    search_keyword = input('Enter your search keyword: ')
    res = main(search_keyword)