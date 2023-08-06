from typing import Optional, List, Dict

from state_access.twiz_state import TwizState  # pip dependency
from cobot_core.apl.utils.documents.base_apl_document import BaseAplDocument

from customAPLs.twiz_detail import TwizTextDetailItem, TwizDetailAplDocument, DetailAplWithVideo
from customAPLs.twiz_image_list import TwizImageListAplDocument, TwizImageListItem
from customAPLs.twiz_text_list import TwizTextListAplDocument, TwizTextListItem
from customAPLs.twiz_video_apl import VideoAplDocumentWithBackgroundImage


class ResponseGeneratorAPLBuilder:

    def run(self, twiz_state: TwizState) -> Optional[List[dict]]:
        """
        TODO: This method is the only one meant to be overwritten. Each RG will generate a different apl screen here
        calling the aux methods available in this class.

        :param twiz_state: Access to the DB values
        :return: an array with the built document and/or necessary directives

        It should follow the following structure:
            1) Access twiz_state to figure out specific context aware values
            2) Call Aux static methods available in this class to generate the APL documents.
                Hint: All aux methods will begin with 'super()._get_'.

                Example: apl_doc = super()._get_detail_document(header_title="Example RG APL Builder")
            3) return apl_doc.build_document()
                No need to ever pass any parameters on the build document method
        """

    # ----- AUX METHODS TO CREATE APL DOCS ----- #

    @staticmethod
    def add_additional_apl_attributes(built_doc: dict, hint_text_prefix: Optional[str] = None,
                                      hint_text: Optional[str] = None,
                                      header_image: Optional[str] = None,
                                      header_subtitle: Optional[str] = None) -> dict:
        """
        This method allows extra attributes to be added to the default TWIZ documents. Any optional parameter which is
        left blank if disregarded. A.k.a. will not affect the appearance of the document.

        WARNING: the tips do not fit on smaller screens, using a header_image also covers the secondary text

        :param built_doc: apl document after the .build_document() call
        :param hint_text_prefix: Prefix to the hint text. Hint format: hint_text_prefix Try "Alexa hint_text"
        :param hint_text: hint text to appear at the bottom of the document
        :param header_image: image url source to add to the left of the document's header
        :param header_subtitle: subtitle to add to the document's header. Note: some document types already offer this
        option when creating it. In that case, do not use this parameter to avoid conflicts and overwriting.

        :return: previously built document with requested adjustments
        """
        if header_subtitle:  # it might not be seen
            built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('headerSubtitle', header_subtitle)

        if hint_text:
            # only supports a single line hint
            built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('hintText',
                                                                                  hint_text_prefix + ' ${data.properties.hintText}')
            # changing the font is not a good solution
            # built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('hintText',
            #                                                                      '<span fontSize = "30dp"\> ' + hint_text_prefix + " ${data.properties.hintText} ")

            # we use transformers for the hint text. textToHint transformer will bring the right wake up word "Try,
            # Alexa/Computer/Echo etc.." We know that Ziggy is not supported yet.
            transformers = [{
                "inputPath": "hintText",
                "transformer": "textToHint"
            }]
            built_doc.get('datasources').get('data').__setitem__('transformers', transformers)
            properties = {
                "hintText": hint_text
            }
            built_doc.get('datasources').get('data').__setitem__('properties', properties)

        if header_image:
            built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('headerAttributionImage',
                                                                                  header_image)

        # if header_image or header_subtitle:
        built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('imageRoundedCorner', True)
        built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('headerAttributionPrimacy', False)
        built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('imageAspectRatio', "square")
        built_doc.get('document').get('mainTemplate')["items"][0].__setitem__('imageScale', "best-fill")
        built_doc.get('document').get('mainTemplate')["items"][0]["imageMetadataPrimacy"] = False

        return built_doc

    # --- DETAIL DOCS --- #
    @staticmethod
    def _get_detail_document_(header_title: str = '', background_image_source: str = '', primary_text: str = '',
                              secondary_text: str = '', image_source: str = '', rating_val: Optional[float] = None,
                              rating_type: str = 'multiple', rating_graphic_type: str = 'AVG',
                              header_back_button: bool = False, image_alignment: str = 'right', image_caption: str = '',
                              detail_type: str = '',
                              body_text: str = '', button_1_text: str = '', button_2_text: str = '',
                              header_subtitle: str = '', background_blurred: bool = False, aspect_ratio='square') \
            -> TwizDetailAplDocument:

        """
        This method will return a DETAIL DOCUMENT with a static background image.
        """

        detail_document = TwizDetailAplDocument()
        detail_document.add_header_title(header_title)
        detail_document.add_background_image_source(background_image_source)

        doc_item = TwizTextDetailItem(primary_text=primary_text, secondary_text=secondary_text,
                                      image_source=image_source, rating_val=rating_val,
                                      rating_type=rating_type,
                                      rating_graphic_type=rating_graphic_type,
                                      header_back_button=header_back_button,
                                      image_alignment=image_alignment, image_caption=image_caption,
                                      detail_type=detail_type, body_text=body_text,
                                      button_1_text=button_1_text,
                                      button_2_text=button_2_text, header_subtitle=header_subtitle,
                                      background_blurred=background_blurred, aspect_ratio=aspect_ratio)

        detail_document.add_item(doc_item)
        return detail_document

    # --- VIDEO DETAIL DOCS --- #
    @staticmethod
    def _get_video_detail_document_(idle_timeout: int = 900000, header_title: str = '',
                                    background_video_source: str = '', thumbnail_img_source: Optional[str] = None,
                                    video_repeat: bool = True, autoplay: bool = True,
                                    primary_text: str = '', secondary_text: str = '',
                                    image_source: str = '', rating_val: Optional[float] = None,
                                    rating_type: str = 'multiple', rating_graphic_type: str = 'AVG',
                                    header_back_button: bool = False, image_alignment: str = 'right',
                                    image_caption: str = '', detail_type: str = '', body_text: str = '',
                                    button_1_text: str = '', button_2_text: str = '', header_subtitle: str = '',
                                    background_blurred: bool = False, aspect_ratio='square') -> BaseAplDocument:

        """
        This method will return a DETAIL DOCUMENT with a video background.
        """

        video_document = DetailAplWithVideo(video_url=background_video_source, thumbnail_img_url=thumbnail_img_source,
                                            blurred=background_blurred, video_repeat=video_repeat, autoplay=autoplay) \
            .set_idle_timeout(idle_timeout)

        video_document.add_header_title(header_title)

        doc_item = TwizTextDetailItem(primary_text=primary_text, secondary_text=secondary_text,
                                      image_source=image_source, rating_val=rating_val,
                                      rating_type=rating_type,
                                      rating_graphic_type=rating_graphic_type,
                                      header_back_button=header_back_button,
                                      image_alignment=image_alignment, image_caption=image_caption,
                                      detail_type=detail_type, body_text=body_text,
                                      button_1_text=button_1_text,
                                      button_2_text=button_2_text, header_subtitle=header_subtitle,
                                      background_blurred=background_blurred, aspect_ratio=aspect_ratio)

        video_document.add_item(doc_item)
        return video_document

    # --- IMAGE LIST DOCS --- #
    @staticmethod
    def _get_image_list_document_(header_title: str = '', background_image_source: str = '',
                                  item_list: List[TwizImageListItem] = None) -> BaseAplDocument:

        """
        This method will return an IMAGE LIST DOCUMENT. Important: It must receive a list of IMAGE LIST ITEMS to then
        iterate and add to the document. Use the _image_list_item_(...) method to create each list item.
        """

        image_list_document = TwizImageListAplDocument()
        image_list_document.add_header_title(header_title)
        image_list_document.add_background_image_source(background_image_source)

        for doc_item in item_list:
            image_list_document.add_item(doc_item)
        return image_list_document

    @staticmethod
    def _get_image_list_item_(primary_text: str = '', secondary_text: str = '', image_source: str = '',
                              rating_val: Optional[float] = None, rating_type: str = 'multiple',
                              rating_graphic_type: str = 'AVG',
                              header_back_button: bool = False, image_text: str = '', header_subtitle: str = '') \
            -> TwizImageListItem:

        """
        This method returns a SINGLE ITEM for an IMAGE LIST DOCUMENT. It is meant to be used to create and return an
        item to later add it to a list of IMAGE LIST ITEMS. This list should then be used as a parameter in the
        _image_list_document_(...) method.
        """

        doc_item = TwizImageListItem(primary_text=primary_text, secondary_text=secondary_text,
                                     image_source=image_source, rating_val=rating_val, rating_type=rating_type,
                                     rating_graphic_type=rating_graphic_type, header_back_button=header_back_button,
                                     image_text=image_text, header_subtitle=header_subtitle)
        return doc_item

    # --- TEXT LIST DOCS --- #
    @staticmethod
    def _get_text_list_document_(header_title: str = '', background_image_source: str = '',
                                 item_list: List[dict] = None) -> BaseAplDocument:

        """
        This method will return a TEXT LIST DOCUMENT. Important: It must receive a list of TEXT LIST ITEMS to then
        iterate and add to the document. Use the _text_list_item_(...) method to create each list item.
        """

        text_list_document = TwizTextListAplDocument()
        text_list_document.add_header_title(header_title)
        text_list_document.add_background_image_source(background_image_source)

        for doc_item in item_list:  # Item structure: [item_primary_text, ]
            text_list_document.add_item(doc_item)
        return text_list_document

    @staticmethod
    def _get_text_list_item_(primary_text: str = '', secondary_text: str = '', image_source: str = '',
                             header_back_button: bool = False, header_subtitle: str = '',
                             hide_ordinal=False) -> TwizTextListItem:

        """
        This method returns a SINGLE ITEM for a TEXT LIST DOCUMENT. It is meant to be used to create and return an
        item to later add it to a list of TEXT LIST ITEMS. This list should then be used as a parameter in the
        _text_list_document_(...) method.
        """

        doc_item = TwizTextListItem(primary_text=primary_text, secondary_text=secondary_text, image_source=image_source,
                                    header_back_button=header_back_button,
                                    header_subtitle=header_subtitle, hide_ordinal=hide_ordinal)

        return doc_item

    # --- VIDEO DOCS --- #
    @staticmethod
    def _get_full_video_document_(idle_timeout: int = 900000, autoplay: bool = True, video_source: str = '',
                                  mute: bool = True, background_image: str = '', remove_on_end_event: bool = False,
                                  blurred: bool = False) -> VideoAplDocumentWithBackgroundImage:

        """
        This method returns a VIDEO DOCUMENT with a static background image and the video controls.
        """

        video_document = VideoAplDocumentWithBackgroundImage(autoplay=autoplay, video_source=video_source,
                                                             mute=mute, background_image=background_image,
                                                             remove_on_end_event=remove_on_end_event,
                                                             blurred=blurred).set_idle_timeout(idle_timeout)
        return video_document
