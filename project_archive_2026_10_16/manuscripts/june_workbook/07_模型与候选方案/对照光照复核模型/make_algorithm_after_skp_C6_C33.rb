# Run this script in SketchUp after opening baseline_original_full_site.skp.
# It keeps the full site in place and only scales the C6 and C33 building groups vertically.
# C6: 6.0m -> 4.5m, scale 0.75
# C33: 9.0m -> 6.75m, scale 0.75

model = Sketchup.active_model
model.start_operation('AI conservative C6 C33 height reduction', true)

targets = {
  'C6' => 0.75,
  'C33' => 0.75
}

changed = []

matcher = lambda do |entity, building_id|
  names = []
  names << entity.name if entity.respond_to?(:name)
  if entity.respond_to?(:definition) && entity.definition
    names << entity.definition.name
  end
  names.compact.any? do |name|
    name.match?(/(^|[^A-Za-z0-9])#{building_id}(_|[^A-Za-z0-9]|$)/)
  end
end

walk_entities = lambda do |entities, &block|
  entities.each do |entity|
    block.call(entity)
    if entity.respond_to?(:definition) && entity.definition
      walk_entities.call(entity.definition.entities, &block)
    elsif entity.respond_to?(:entities)
      walk_entities.call(entity.entities, &block)
    end
  end
end

walk_entities.call(model.entities) do |entity|
  next unless entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)

  targets.each do |building_id, scale_z|
    next unless matcher.call(entity, building_id)

    entity.make_unique if entity.respond_to?(:make_unique)
    bounds = entity.bounds
    base = Geom::Point3d.new(bounds.center.x, bounds.center.y, bounds.min.z)
    transform = Geom::Transformation.scaling(base, 1.0, 1.0, scale_z)
    entity.transform!(transform)
    changed << "#{building_id}: #{entity.name.empty? ? entity.definition.name : entity.name}"
    break
  end
end

model.commit_operation

output = File.join(File.dirname(model.path), 'algorithm_after_full_site_only_C6_C33_changed.skp')
model.save(output)

UI.messagebox("Saved algorithm-after SKP:\n#{output}\n\nChanged groups:\n#{changed.uniq.join("\n")}")
