# Marquedown

Extending Markdown further by adding a few more useful notations.
It can be used in place of `markdown` as it also uses and applies it.

## Examples

### Blockquote with citation

This is currently limited to the top scope with no indentation.
Surrounding dotted lines are optional.

```md
......................................................
> You have enemies? Good. That means you've stood up
> for something, sometime in your life.
-- Winston Churchill
''''''''''''''''''''''''''''''''''''''''''''''''''''''
```

```html
<blockquote>
    <p>
        You have enemies? Good. That means you've stood up
        for something, sometime in your life.
    </p>
    <cite>Winston Churchill</cite>
</blockquote>
```

### Embed video

#### YouTube

```md
![dimweb](https://youtu.be/VmAEkV5AYSQ "An embedded YouTube video")
```

```html
<iframe
    src="https://www.youtube.com/embed/VmAEkV5AYSQ"
    title="An embedded YouTube video" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen>
</iframe>
```

### BBCode HTML tags

These tags allow you to put Marquedown inside HTML tags. This is done by finding and replacing them with their represented HTML after all other Marquedown has been rendered.

#### Tags and classes

The naming scheme is the same as in CSS, e.g. `tag.class1.class2`
If `tag` is omitted, it is treated to be `div`

#### ID:s

ID:s are supported using `#beans` at the end of the tag, ex. `[p#beans]`

```md
[section]
[.bingo]
A regular **paragraph** written in Marquedown, but *within* other HTML tags.
[//]

[tag.class1.class2] [/tag]
```

```html
<section>
<div class="bingo">
    <p>
        A regular <strong>paragraph</strong> written in Marquedown, but <em>within</em> other HTML tags.
    </p>
</div></section>

<tag class="class1 class2"> </tag>
```

### Label list

```md
(| email: [jon@webby.net](mailto:jon@webby.net)
(| matrix: [@jon:webby.net](https://matrix.to/#/@jon:webby.net)
(| runescape: jonathan_superstar1777
```

```html
<ul class="labels">
    <li class="label label-email">
        <a href="mailto:jon@webby.net">
            jon@webby.net
        </a>
    </li>
    <li class="label label-matrix">
        <a href="https://matrix.to/#/@jon:webby.net">
            @jon:webby.net
        </a>
    </li>
    <li class="label label-runescape">
        jonathan_superstar1777
    </li>
</ul>
```

## Commands

### `render`: Render documents

You can render an entire directory and its subdirectories of Markdown or Marquedown documents. This can be used to automate rendering pages for your website.

Do `python -m marquedown render --help` for list of options.

#### Example

For a few of my websites hosted on GitLab, I have it set up to run *this* on push:

```sh
# Render document
python -m marquedown render -i ./md -o ./public -t ./templates/page.html

# This is for the GitLab Pages publication
mkdir .public
cp -r public .public
mv .public public  
```