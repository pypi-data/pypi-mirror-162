import os

class TermSpark:
    left = ''
    right = ''
    center = ''
    separator = ' '
    line_is_set = False
    colors_codes = [
        '[30m', # grey
        '[31m', # red
        '[32m', # green
        '[33m', # yellow
        '[0m',  # reset
    ]
    placements = [
        'left',
        'right',
        'center',
    ]

    def print_left(self, string):
        self.left = string

        return self

    def print_right(self, string):
        self.right = string

        return self

    def print_center(self, string):
        self.center = string

        return self

    def set_separator(self, separator):
        if separator: self.separator = separator[0]

        return self

    def calculate_separator_length(self):
        colors_codes_length = self.calculate_colors_codes_length()
        content_length = 0

        for placement in self.placements:
            content_length += len(getattr(self, placement))
        self.separator_length = os.get_terminal_size()[0] - content_length + colors_codes_length

    def calculate_colors_codes_length(self):
        colors_codes_length = 0

        for color_code in self.colors_codes:
            for placement in self.placements:
                placement_content = getattr(self, placement)
                if color_code in placement_content:
                    colors_codes_length += (len(color_code) * placement_content.count(color_code)) + placement_content.count(color_code)

        return colors_codes_length

    def line(self, separator = None):
        self.line_is_set = True
        self.set_separator(separator)
        return self

    def __del__(self):
        self.calculate_separator_length()
        separator_mid_width = self.separator * int( self.separator_length / 2 )

        if self.left or self.right or self.center or self.line_is_set:
            if self.center:
                center = separator_mid_width + self.center + separator_mid_width
            else:
                center = self.separator * self.separator_length
            print(self.left + center + self.right)