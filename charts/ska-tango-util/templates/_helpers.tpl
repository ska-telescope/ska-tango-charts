{{ define "ska-tango-util.dsconfig-properties.tpl" -}}
{{- $out := dict }}

{{- if hasKey $.props_obj "properties" }}
  {{- $properties := dict }}
  {{- range $property := $.props_obj.properties }}
    {{- $values := list }}
    {{- range $value := $property.values }}
      {{- $values = append $values (tpl $value $.chart) }}
    {{- end }}
    {{- $_ := set $properties $property.name $values }}
  {{- end }}
  {{- $_ := set $out "properties" $properties}}
{{- end }}

{{- if hasKey $.props_obj "attribute_properties" }}
  {{- $attribute_properties := dict }}
  {{- range $attr_prop := $.props_obj.attribute_properties }}
    {{- $properties := dict }}
    {{- range $property := $attr_prop.properties }}
      {{- $values := list }}
      {{- range $value := $property.values }}
        {{- $values = append $values (tpl $value $.chart) }}
      {{- end }}
      {{- $_ := set $properties $property.name $values }}
    {{- end }}
    {{- $_ := set $attribute_properties $attr_prop.attribute $properties }}
  {{- end }}
  {{- $_ := set $out "attribute_properties" $attribute_properties }}
{{- end }}

{{- $out | toPrettyJson }}

{{- end }}
