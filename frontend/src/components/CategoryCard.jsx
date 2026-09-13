function CategoryCard({ icon, label, description, onClick }) {
  return (
    <div className="category-card" onClick={onClick}>
      <span className="icon">{icon}</span>
      <span className="label">{label}</span>
      {description && (
        <p style={{ fontSize: '0.75rem', color: '#475569', marginTop: '6px' }}>
          {description}
        </p>
      )}
    </div>
  )
}

export default CategoryCard
